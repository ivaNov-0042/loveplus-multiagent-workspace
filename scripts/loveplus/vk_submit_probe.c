/* 最小 Vulkan 提交探针：不建窗口、不建表面（不碰 WSI）。
 * 目的：区分"dzn 核心提交坏了"与"只有呈现路径坏"。
 * 步骤：实例 → 选 D3D12 设备 → 逻辑设备 → host-visible buffer → 提交空命令缓冲 → 等 fence。
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <vulkan/vulkan.h>

#define CK(x)                                                        \
    do {                                                             \
        VkResult r_ = (x);                                            \
        if (r_ != VK_SUCCESS) {                                       \
            printf("FAIL %-45s -> VkResult %d\n", #x, (int)r_);       \
            return 1;                                                 \
        }                                                            \
        printf("ok   %s\n", #x);                                      \
    } while (0)

int main(void) {
    VkApplicationInfo ai = {VK_STRUCTURE_TYPE_APPLICATION_INFO};
    ai.pApplicationName = "vk_submit_probe";
    ai.apiVersion = VK_API_VERSION_1_1;

    VkInstanceCreateInfo ici = {VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};
    ici.pApplicationInfo = &ai;

    VkInstance inst;
    CK(vkCreateInstance(&ici, NULL, &inst));

    uint32_t n = 0;
    CK(vkEnumeratePhysicalDevices(inst, &n, NULL));
    printf("     physical devices = %u\n", n);
    if (n == 0) return 1;
    VkPhysicalDevice *pds = calloc(n, sizeof(*pds));
    CK(vkEnumeratePhysicalDevices(inst, &n, pds));

    int chosen = -1;
    for (uint32_t i = 0; i < n; i++) {
        VkPhysicalDeviceProperties p;
        vkGetPhysicalDeviceProperties(pds[i], &p);
        printf("     [%u] %s\n", i, p.deviceName);
        if (strstr(p.deviceName, "Direct3D12") && chosen < 0) chosen = (int)i;
    }
    if (chosen < 0) {
        printf("     no Direct3D12 device found\n");
        return 1;
    }
    printf("     -> using [%d]\n", chosen);

    uint32_t qn = 0;
    vkGetPhysicalDeviceQueueFamilyProperties(pds[chosen], &qn, NULL);
    VkQueueFamilyProperties *qps = calloc(qn, sizeof(*qps));
    vkGetPhysicalDeviceQueueFamilyProperties(pds[chosen], &qn, qps);
    int qf = -1;
    for (uint32_t i = 0; i < qn; i++) {
        if (qps[i].queueFlags & (VK_QUEUE_GRAPHICS_BIT | VK_QUEUE_COMPUTE_BIT)) {
            qf = (int)i;
            break;
        }
    }
    if (qf < 0) return 1;

    float prio = 1.0f;
    VkDeviceQueueCreateInfo dqci = {VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO};
    dqci.queueFamilyIndex = (uint32_t)qf;
    dqci.queueCount = 1;
    dqci.pQueuePriorities = &prio;
    VkDeviceCreateInfo dci = {VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO};
    dci.queueCreateInfoCount = 1;
    dci.pQueueCreateInfos = &dqci;

    VkDevice dev;
    CK(vkCreateDevice(pds[chosen], &dci, NULL, &dev));

    VkQueue q;
    vkGetDeviceQueue(dev, (uint32_t)qf, 0, &q);

    VkBufferCreateInfo bci = {VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO};
    bci.size = 4096;
    bci.usage = VK_BUFFER_USAGE_TRANSFER_SRC_BIT | VK_BUFFER_USAGE_TRANSFER_DST_BIT;
    bci.sharingMode = VK_SHARING_MODE_EXCLUSIVE;
    VkBuffer buf;
    CK(vkCreateBuffer(dev, &bci, NULL, &buf));

    VkMemoryRequirements mr;
    vkGetBufferMemoryRequirements(dev, buf, &mr);
    VkPhysicalDeviceMemoryProperties mp;
    vkGetPhysicalDeviceMemoryProperties(pds[chosen], &mp);
    uint32_t mt = ~0u;
    for (uint32_t i = 0; i < mp.memoryTypeCount; i++) {
        if ((mr.memoryTypeBits & (1u << i)) &&
            (mp.memoryTypes[i].propertyFlags &
             (VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT)) ==
                (VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT | VK_MEMORY_PROPERTY_HOST_COHERENT_BIT)) {
            mt = i;
            break;
        }
    }
    if (mt == ~0u) {
        printf("FAIL no host-visible memory type\n");
        return 1;
    }

    VkMemoryAllocateInfo mai = {VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO};
    mai.allocationSize = mr.size;
    mai.memoryTypeIndex = mt;
    VkDeviceMemory mem;
    CK(vkAllocateMemory(dev, &mai, NULL, &mem));
    CK(vkBindBufferMemory(dev, buf, mem, 0));

    VkCommandPoolCreateInfo pci = {VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO};
    pci.queueFamilyIndex = (uint32_t)qf;
    VkCommandPool pool;
    CK(vkCreateCommandPool(dev, &pci, NULL, &pool));

    VkCommandBufferAllocateInfo cbai = {VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO};
    cbai.commandPool = pool;
    cbai.level = VK_COMMAND_BUFFER_LEVEL_PRIMARY;
    cbai.commandBufferCount = 1;
    VkCommandBuffer cb;
    CK(vkAllocateCommandBuffers(dev, &cbai, &cb));

    VkFenceCreateInfo fci = {VK_STRUCTURE_TYPE_FENCE_CREATE_INFO};
    VkFence fence;
    CK(vkCreateFence(dev, &fci, NULL, &fence));
    VkFenceCreateInfo fci2 = {VK_STRUCTURE_TYPE_FENCE_CREATE_INFO};
    VkFence fence2;
    CK(vkCreateFence(dev, &fci2, NULL, &fence2));

    /* 3 轮：空命令缓冲 + 4 字节拷贝，各自等待 */
    for (int round = 1; round <= 3; round++) {
        VkCommandBufferBeginInfo bi = {VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO};
        bi.flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT;
        CK(vkBeginCommandBuffer(cb, &bi));
        VkBufferCopy region = {0, 0, 4};
        vkCmdCopyBuffer(cb, buf, buf, 1, &region);
        CK(vkEndCommandBuffer(cb));

        VkSubmitInfo si = {VK_STRUCTURE_TYPE_SUBMIT_INFO};
        si.commandBufferCount = 1;
        si.pCommandBuffers = &cb;
        VkResult sr = vkQueueSubmit(q, 1, &si, fence);
        if (sr != VK_SUCCESS) {
            printf("FAIL vkQueueSubmit round %d -> VkResult %d\n", round, (int)sr);
            return 1;
        }
        printf("ok   vkQueueSubmit round %d\n", round);

        VkResult wr = vkWaitForFences(dev, 1, &fence, VK_TRUE, 5000000000ull);
        if (wr != VK_SUCCESS) {
            printf("FAIL vkWaitForFences round %d -> VkResult %d\n", round, (int)wr);
            return 1;
        }
        printf("ok   vkWaitForFences round %d (5s 内完成)\n", round);
        CK(vkResetFences(dev, 1, &fence));
        CK(vkResetCommandBuffer(cb, 0));
    }

    /* 队列是否已经被移除 */
    VkResult idle = vkQueueWaitIdle(q);
    printf("vkQueueWaitIdle -> %d (%s)\n", (int)idle, idle == VK_SUCCESS ? "OK" : "非成功");

    CK(vkDeviceWaitIdle(dev));
    vkDestroyFence(dev, fence2, NULL);
    vkDestroyFence(dev, fence, NULL);
    vkDestroyCommandPool(dev, pool, NULL);
    vkDestroyBuffer(dev, buf, NULL);
    vkFreeMemory(dev, mem, NULL);
    vkDestroyDevice(dev, NULL);
    vkDestroyInstance(inst, NULL);
    printf("\nRESULT: dzn 的核心提交路径可用（无窗口/无表面）\n");
    return 0;
}
