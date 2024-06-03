#include <string.h>
#include <stdio.h>
#include <stdarg.h>
#include <Windows.h>
#include "BdshemuCaller.hpp"

extern "C" {
#if !defined(BDDISASM_HAS_VSNPRINTF)
    //
    // nd_vsnprintf
    //
    int
        nd_vsnprintf_s(
            char* buffer,
            size_t sizeOfBuffer,
            size_t count,
            const char* format,
            va_list argptr
        )
    {
        return _vsnprintf_s(buffer, sizeOfBuffer, count, format, argptr);
    }
#endif // !defined(BDDISASM_HAS_VSNPRINTF)

#if !defined(BDDISASM_HAS_MEMSET)
    void*
        nd_memset(void* s, int c, size_t n)
    {
        return memset(s, c, n);
    }
#endif // !defined(BDDISASM_HAS_MEMSET)
}

ND_BOOL
MemAccess(
    void* ShemuContext, // Shemu emulation context.
    ND_UINT64 Gla,      // Linear address to be accessed.
    ND_SIZET Size,      // Number of bytes to access.
    ND_UINT8* Buffer,   // Contains the read content (if Store is false), or the value to be stored at Gla.
    ND_BOOL Store       // If false, read content at Gla. Otherwise, write content at Gla.
)
{
    return true;
}

int
AnalyzeShellcode(unsigned char* Shellcode, uint32_t Size, bool Is32Bit, unsigned int* ShemuStatus, uint64_t* Flags)
{
    Status status = Status::Unsuccessful;
    uint64_t shellcodeAddress = reinterpret_cast<uint64_t>(Shellcode);
    uint8_t* stack = nullptr;
    uint8_t* internalBuffer = nullptr;
    size_t internalBufferSize = 0;

    SHEMU_CONTEXT* ctx = reinterpret_cast<SHEMU_CONTEXT*>(malloc(sizeof(SHEMU_CONTEXT)));
    if (!ctx)
    {
        status = Status::MallocFailed;
        goto cleanup;
    }
    memset(ctx, 0, sizeof(SHEMU_CONTEXT));

    // set shellcode address
    ctx->Shellcode = reinterpret_cast<ND_UINT8*>(shellcodeAddress);

    // base must be on 32 bits if the shellcode is of 32 bits
    ctx->ShellcodeBase = (Is32Bit) ? (0xffffffff & shellcodeAddress) : shellcodeAddress;
    ctx->Registers.RegRip = (Is32Bit) ? (0xffffffff & shellcodeAddress) : shellcodeAddress;
    ctx->ShellcodeSize = Size;
    ctx->Ring = 3;
    ctx->Mode = (Is32Bit) ? ND_CODE_32 : ND_CODE_64;
    ctx->StackSize = 0x2000;
    stack = reinterpret_cast<uint8_t*>(malloc(ctx->StackSize));
    if (!stack)
    {
        status = Status::MallocFailed;
        goto cleanup;
    }

    ctx->Stack = stack;
    // TODO: Make this safe
    // stack starts at high addresses, so we add Stack + StackSize
    // by decrementing it, we simulate allocating space for variables
    ctx->Registers.RegRsp = reinterpret_cast<uint64_t>(ctx->Stack) + ctx->StackSize - 0x100;
    ctx->StackBase = (Is32Bit) ? (0xffffffff & reinterpret_cast<uint64_t>(stack)) : reinterpret_cast<uint64_t>(stack);

    // TODO: Make this safe
    internalBufferSize = Size + ctx->StackSize;
    internalBuffer = reinterpret_cast<uint8_t*>(malloc(internalBufferSize));
    if (!internalBuffer)
    {
        status = Status::MallocFailed;
    }

    ctx->Intbuf = internalBuffer;
    ctx->IntbufSize = internalBufferSize;
    memset(ctx->Intbuf, 0, internalBufferSize);

    ctx->MaxInstructionsCount = 1000;
    ctx->NopThreshold = 75;
    ctx->StrThreshold = 8;
    ctx->MemThreshold = 100;

    ctx->Registers.RegCr0 = 0x80050031;
    ctx->Registers.RegCr2 = 0;
    ctx->Registers.RegCr3 = 0x1aa000;
    ctx->Registers.RegCr4 = 0x170678;
    ctx->Registers.RegFlags = 0x202;

    if (ctx->Mode == ND_CODE_64)
    {
        ctx->Segments.Cs.Selector = (ctx->Ring == 3) ? 0x33 : 0x10;
        ctx->Segments.Ds.Selector = (ctx->Ring == 3) ? 0x2b : 0x18;
        ctx->Segments.Es.Selector = (ctx->Ring == 3) ? 0x2b : 0x18;
        ctx->Segments.Ss.Selector = (ctx->Ring == 3) ? 0x2b : 0x18;
        ctx->Segments.Fs.Selector = (ctx->Ring == 3) ? 0x2b : 0x00;
        ctx->Segments.Gs.Selector = (ctx->Ring == 3) ? 0x53 : 0x00;

        ctx->Segments.Fs.Base = 0;
        ctx->Segments.Gs.Base = 0;
        ctx->TibBase = ctx->Segments.Gs.Base;
    }
    else
    {
        ctx->Segments.Cs.Selector = (ctx->Ring == 3) ? 0x1b : 0x08;
        ctx->Segments.Ds.Selector = (ctx->Ring == 3) ? 0x23 : 0x10;
        ctx->Segments.Es.Selector = (ctx->Ring == 3) ? 0x23 : 0x10;
        ctx->Segments.Ss.Selector = (ctx->Ring == 3) ? 0x23 : 0x10;
        ctx->Segments.Fs.Selector = (ctx->Ring == 3) ? 0x3b : 0x30;
        ctx->Segments.Gs.Selector = (ctx->Ring == 3) ? 0x23 : 0x00;

        ctx->Segments.Fs.Base = 0;
        ctx->Segments.Gs.Base = 0;
        ctx->TibBase = ctx->Segments.Fs.Base;
    }

    ctx->AccessMemory = MemAccess;

    *ShemuStatus = ShemuEmulate(ctx);
    *Flags = ctx->Flags;
    status = Status::Success;
cleanup:
    if (internalBuffer)
    {
        free(internalBuffer);
    }
    if (stack)
    {
        free(stack);
    }
    if (ctx)
    {
        free(ctx);
    }
    return static_cast<int>(status);
}

const char* gSpaces[16] =
{
    "",
    "  ",
    "    ",
    "      ",
    "        ",
    "          ",
    "            ",
    "              ",
    "                ",
    "                  ",
    "                    ",
    "                      ",
    "                        ",
    "                          ",
    "                            ",
    "                              ",
};

void
print_instruction(
    __in SIZE_T Rip,
    __in PINSTRUX Instrux,
    __in char* Buffer,
    __in uint64_t BufSize
)
{
    char instruxText[ND_MIN_BUF_SIZE];
    DWORD k = 0, idx = 0, i = 0;
    CHAR tempBuf[1000] = { 0 };

    sprintf_s(tempBuf, 1000, "%p ", (void*)(Rip));
    strcat_s(Buffer, BufSize, tempBuf);
    RtlZeroMemory(tempBuf, 1000);

    for (; k < Instrux->Length; k++)
    {
        sprintf_s(tempBuf, 1000, "%02x", Instrux->InstructionBytes[k]);
        strcat_s(Buffer, BufSize, tempBuf);
        RtlZeroMemory(tempBuf, 1000);
    }

    sprintf_s(tempBuf, 1000, "%s", gSpaces[16 - (Instrux->Length & 0xF)]);
    strcat_s(Buffer, BufSize, tempBuf);
    RtlZeroMemory(tempBuf, 1000);

    NdToText(Instrux, Rip, ND_MIN_BUF_SIZE, instruxText);

    sprintf_s(tempBuf, 1000, "%s\n", instruxText);
    strcat_s(Buffer, BufSize, tempBuf);
    RtlZeroMemory(tempBuf, 1000);
}

int
DisassembleShellcode(unsigned char* Shellcode, uint32_t Size, bool Is32Bit, char* Buffer, uint64_t BufSize)
{
    Shellcode;
    Size;
    Is32Bit;
    Buffer;
    BufSize;

    // code copied from disasmtool
    INSTRUX instrux;
    ND_CONTEXT ctx = { 0 };
    unsigned long long icount = 0, istart, iend, start, end, itotal = 0, tilen = 0, ticount = 0;
    SIZE_T rip, fsize = Size;
    PBYTE buffer = Shellcode;
    CHAR tempBuf[1000] = { 0 };

    NdInitContext(&ctx);

    ctx.DefCode = Is32Bit ? ND_CODE_32 : ND_CODE_64;
    ctx.DefData = Is32Bit ? ND_CODE_32 : ND_CODE_64;
    ctx.DefStack = Is32Bit ? ND_CODE_32 : ND_CODE_64;
    ctx.VendMode = ND_VEND_ANY; // DON'T CARE
    ctx.FeatMode = ND_FEAT_ALL;

    // Disassemble
    rip = 0;
    while (rip < Size)
    {
        NDSTATUS status;

        icount++;

#if defined(ND_ARCH_X86) || defined(ND_ARCH_X64)
        istart = __rdtsc();
#else
        istart = 0;
#endif

        status = NdDecodeWithContext(&instrux, buffer + rip, fsize - rip, &ctx);

#if defined(ND_ARCH_X86) || defined(ND_ARCH_X64)
        iend = __rdtsc();
#else
        iend = 1;
#endif

        itotal += iend - istart;
        if (!ND_SUCCESS(status))
        {
            sprintf_s(tempBuf, 1000, "%p ", (void*)(rip));
            strcat_s(Buffer, BufSize, tempBuf);
            RtlZeroMemory(tempBuf, 1000);

            sprintf_s(tempBuf, 1000, "%02x", buffer[rip]);
            strcat_s(Buffer, BufSize, tempBuf);
            RtlZeroMemory(tempBuf, 1000);

            sprintf_s(tempBuf, 1000, "%s", gSpaces[16 - 1]);
            strcat_s(Buffer, BufSize, tempBuf);
            RtlZeroMemory(tempBuf, 1000);

            sprintf_s(tempBuf, 1000, "db 0x%02x (0x%08x)\n", buffer[rip], status);
            strcat_s(Buffer, BufSize, tempBuf);
            RtlZeroMemory(tempBuf, 1000);

            rip++;
        }
        else
        {
            tilen += instrux.Length;
            ticount++;

            print_instruction(rip, &instrux, Buffer, BufSize);

            rip += instrux.Length;
        }
    }
    return 99;
}