/*
 * siren_ref.c —— 用 FFmpeg 的 G.722.1(siren) 解码器解「裸帧」，产出 float32 单声道 PCM。
 *
 * 为什么需要它：NLP+ 的 Siren14Voice.spp 是裸帧拼接（每帧 46B，无容器头），
 * 没有 demuxer 能喂进 ffmpeg CLI；而 libavcodec 的 API 可以直接 send_packet 裸帧。
 * 本程序就是做这件事的最小 harness，用作移植到 Python 的逐样本参照。
 *
 * 构建（见 scripts/loveplus/SCRIPTS.md）：
 *   cd /tmp/ffsrc/ffmpeg-6.1.1 && ./configure --disable-everything --disable-programs \
 *     --disable-doc --disable-network --disable-autodetect --disable-asm --disable-x86asm \
 *     --enable-decoder=siren && make -j
 *   cc -O2 -o siren_ref siren_ref.c -I/tmp/ffsrc/ffmpeg-6.1.1 \
 *      /tmp/ffsrc/ffmpeg-6.1.1/libavcodec/libavcodec.a /tmp/ffsrc/ffmpeg-6.1.1/libavutil/libavutil.a \
 *      -lm -lpthread -lz
 *
 * 用法：
 *   ./siren_ref <in.frames> <frame_bytes> <swap16 0|1> <out.f32> [max_frames]
 * 说明：
 *   swap16=1 表示输入按「16 位小端字」打包（NLP+ .spp 的排布），
 *   程序会先做 16 位字节交换再交给解码器（FFmpeg 按 MSB-first 字节流读）。
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include <libavcodec/avcodec.h>
#include <libavutil/frame.h>

int main(int argc, char **argv)
{
    if (argc < 5) {
        fprintf(stderr, "usage: %s <in.frames> <frame_bytes> <swap16 0|1> <out.f32> [max_frames]\n", argv[0]);
        return 2;
    }
    const char *in_path = argv[1];
    int frame_bytes = atoi(argv[2]);
    int swap16 = atoi(argv[3]);
    const char *out_path = argv[4];
    long max_frames = (argc > 5) ? atol(argv[5]) : -1;

    FILE *fi = fopen(in_path, "rb");
    if (!fi) { perror("open in"); return 1; }
    FILE *fo = fopen(out_path, "wb");
    if (!fo) { perror("open out"); return 1; }

    const AVCodec *codec = avcodec_find_decoder_by_name("siren");
    if (!codec) { fprintf(stderr, "siren decoder not found\n"); return 1; }
    AVCodecContext *c = avcodec_alloc_context3(codec);
    c->sample_rate = 16000;
    if (avcodec_open2(c, codec, NULL) < 0) { fprintf(stderr, "open2 failed\n"); return 1; }

    AVPacket *pkt = av_packet_alloc();
    AVFrame *fr = av_frame_alloc();
    uint8_t *buf = malloc(frame_bytes);
    long n = 0, nfr = 0, nbad = 0;
    long long total = 0;
    int quiet = getenv("SIREN_QUIET") != NULL;
    while (fread(buf, 1, frame_bytes, fi) == (size_t)frame_bytes) {
        if (max_frames > 0 && n >= max_frames) break;
        if (swap16) {
            for (int i = 0; i + 1 < frame_bytes; i += 2) {
                uint8_t t = buf[i]; buf[i] = buf[i + 1]; buf[i + 1] = t;
            }
        }
        av_packet_unref(pkt);
        pkt->data = buf;
        pkt->size = frame_bytes;
        int ret = avcodec_send_packet(c, pkt);
        if (ret < 0) {
            nbad++;
            if (!quiet && nbad <= 10) fprintf(stderr, "  send_packet err %d at frame %ld\n", ret, n);
            avcodec_flush_buffers(c);   /* 跳错继续，只为统计/取好帧 */
            n++;
            continue;
        }
        while ((ret = avcodec_receive_frame(c, fr)) == 0) {
            fwrite(fr->data[0], sizeof(float), fr->nb_samples, fo);
            total += fr->nb_samples;
            nfr++;
        }
        if (ret != AVERROR(EAGAIN) && ret != AVERROR_EOF) {
            nbad++;
            if (!quiet && nbad <= 10) fprintf(stderr, "  receive err %d at frame %ld\n", ret, n);
            avcodec_flush_buffers(c);
        }
        n++;
    }
    fprintf(stderr, "[siren_ref] read %ld frames, ok=%ld bad=%ld samples=%lld\n", n, nfr, nbad, total);
    fclose(fi); fclose(fo);
    av_frame_free(&fr); av_packet_free(&pkt); avcodec_free_context(&c); free(buf);
    return 0;
}
