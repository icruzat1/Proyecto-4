# Firmware inicial de integración. Lee cada precio y responde mantener.
# x1 base SPI, x2 STATUS, x3 ultimo precio, x0 decision mantener.
# STATUS 0x80010000, PRICE 0x80010004, DECISION 0x80010008.
    lui x1, 0x80010
esperar:
    lw x2, 0(x1)
    andi x2, x2, 1
    beq x2, x0, esperar
    lw x3, 4(x1)
    sw x0, 8(x1)
    jal x0, esperar
