import sys
import random
import subprocess
import struct
from math import sqrt, modf, fmod


def right_cyclic_shift(t: int, shift: int):
    for i in range(shift):
        t = (t >> 1 | (0 if int(t / 2) * 2 == t else 1 << 31))
    return t


def check_prime(n: int):
    for i in range(2, max(n, int(sqrt(n)))):
        if int(n / i) * i == n and i != n:
            break
    else:
        return True
    return False


def main(content=None):
    #  (первые 32 бита дробных частей квадратных корней первых восьми простых чисел [от 2 до 19]):

    # TODO use check_prime
    h0 = int(modf(sqrt(2))[0] * (1 << 32))  # 0x6A09E667
    h1 = int(modf(sqrt(3))[0] * (1 << 32))  # 0xBB67AE85
    h2 = int(modf(sqrt(5))[0] * (1 << 32))  # 0x3C6EF372
    h3 = int(modf(sqrt(7))[0] * (1 << 32))  # 0xA54FF53A
    h4 = int(modf(sqrt(11))[0] * (1 << 32))  # 0x510E527F
    h5 = int(modf(sqrt(13))[0] * (1 << 32))  # 0x9B05688C
    h6 = int(modf(sqrt(17))[0] * (1 << 32))  # 0x1F83D9AB
    h7 = int(modf(sqrt(19))[0] * (1 << 32))  # 0x5BE0CD19

    k = []

    for y in range(2, 311 + 1):
        if check_prime(y):
            k.append(int(modf(y ** (1 / 3))[0] * (1 << 32)))

    # k = [0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
    #    0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
    #    0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
    #    0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
    #    0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13, 0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
    #    0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
    #    0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
    #    0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2]

    # print(h0, h1, h2, h3, h4, h5, h6, h7)
    # print(k)

    # TODO add read from stdin

    if content is None:
        with open(sys.argv[1], 'rb') as f:
            content = f.read()


    # L — число бит в сообщении

    L = len(content) * 8
    # print(hex(h0), '\n', hex(h1), '\n', hex(h2), '\n', hex(h3), '\n', hex(h4), '\n', hex(h5), '\n', hex(h6), '\n', hex(h7), )
    # print('\n'.join([str(hex(p)) for p in k]))
    # K is the minimum number >= 0 such that L + 1 + K + 64 is a multiple of 512
    K = 0
    while 1:
        if int((L + 1 + K + 64) / 512) * 512 == (L + 1 + K + 64):
            break
        K += 1
    content += bytes([128])
    for i in range(int((K - 7) / 8)):
        content += bytes([0])
    content += struct.pack('>Q', L)

    # TODO use memory view ?

    i = 0
    msg_len = len(content)

    assert int((msg_len * 8) / 512) * 512 == msg_len * 8

    chunk_len = int(512 / 8)

    # print(msg_len)
    chunk_i = 0
    while chunk_i * chunk_len < msg_len:
        chunk = content[chunk_i * chunk_len :(chunk_i + 1) * chunk_len]
        chunk_i += 1
        w = []
        for pp in range(16):
            t = struct.unpack('>I', chunk[pp * 4: (pp + 1) * 4])[0]
            w.append(t)
        for i in range(16, 64):
            # s0 = (w[i-15] rotr 7) ^ (w[i-15] rotr 18) ^ (w[i-15] >> 3)
            # s1 = (w[i-2] rotr 17) ^ (w[i-2] rotr 19) ^ (w[i-2] >> 10)
            s0 = right_cyclic_shift(w[i - 15], 7) ^ right_cyclic_shift(w[i - 15], 18) ^ (w[i - 15] >> 3)
            s1 = (right_cyclic_shift(w[i - 2], 17)) ^ (right_cyclic_shift(w[i - 2], 19)) ^ (w[i - 2] >> 10)
            w.append(int(fmod(w[i - 16] + s0 + w[i - 7] + s1, 2 ** 32)))  # + это сложение а не конкатенация

        a = h0
        b = h1
        c = h2
        d = h3
        e = h4
        f = h5
        g = h6
        h = h7
        # import pdb;
        # pdb.set_trace()
        # Основной цикл:
        for i in range(63 + 1):
            Σ0 = (right_cyclic_shift(a, 2)) ^ (right_cyclic_shift(a, 13)) ^ (right_cyclic_shift(a, 22))
            Ma = (a & b) ^ (a & c) ^ (b & c)



            # t2 = int(fmod(Σ0 + Ma, 2 ** 32))   # !!!!!!!!!!!!!
            t2 = Σ0 + Ma  # здесь калдывать по модулю рано, так как потом еще добавим слагаемое
            Σ1 = (right_cyclic_shift(e, 6)) ^ (right_cyclic_shift(e, 11)) ^ (right_cyclic_shift(e, 25))
            Ch = (e & f) ^ ((~e) & g)
            # t1 = int(fmod(h + Σ1 + Ch + k[i] + w[i], 2 ** 23))  # + это сложение а не конкатенация !!!!!!!!!!!
            t1 = h + Σ1 + Ch + k[i] + w[i]  # здесь калдывать по модулю рано, так как потом еще добавим слагаемое


            h = g
            g = f
            f = e
            e = int(fmod(d + t1, 2 ** 32))
            d = c
            c = b
            b = a
            a = int(fmod(t1 + t2, 2 ** 32))
            # print(('a', a, '\nb', b, '\nc', c, '\nd', d, '\ne', e, '\nf', f, '\ng', g, '\nh', h))

        # Добавить полученные значения к ранее вычисленному результату:
        h0 = int(fmod(h0 + a, 2 ** 32))
        h1 = int(fmod(h1 + b, 2 ** 32))
        h2 = int(fmod(h2 + c, 2 ** 32))
        h3 = int(fmod(h3 + d, 2 ** 32))
        h4 = int(fmod(h4 + e, 2 ** 32))
        h5 = int(fmod(h5 + f, 2 ** 32))
        h6 = int(fmod(h6 + g, 2 ** 32))
        h7 = int(fmod(h7 + h, 2 ** 32))

    # import pdb; pdb.set_trace()
    # Получить итоговое значение хеша:
    digest = ''.join('{:08X}'.format(a) for a in [h0, h1, h2, h3, h4, h5, h6, h7])
    # print(digest)
    # print(len(digest))
    return digest
    # assert len(digest) == 64
    # assert digest.lower() == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', digest.lower() + ' ' + str(len(digest))


def test():
    with open('test_content', 'wb'):
        pass

    assert main(b'').lower() == subprocess.check_output(['sha256sum', 'test_content']).split(b' ')[0].decode('utf8')

    with open('test_content', 'wb') as f:
        f.write(bytes([random.randint(1, 255) for _ in range(1000000)]))

    with open('test_content', 'rb') as f:
        content = f.read()
    assert main(content).lower() == subprocess.check_output(['sha256sum', 'test_content']).split(b' ')[0].decode('utf8')


if __name__ == '__main__':
    # test()
    main()
