from tack.structures.Tack import Tack
from tack.structures.TackActivation import TackActivation
from tack.structures.TackBreakSig import TackBreakSig
from tack.tls.TlsStructure import TlsStructure
from tack.tls.TlsStructureWriter import TlsStructureWriter

class TackExtension(TlsStructure):

    def __init__(self, data=None):
        TlsStructure.__init__(self, data)
        if data is not None:
            self.tack           = self._parseTack()
            self.break_sigs     = self._parseBreakSigs()
            self.pin_activation = self.getInt(1)

            if self.pin_activation not in TackActivation.ALL:
                raise SyntaxError("Bad pin_activation value")

            if self.index != len(data):
                raise SyntaxError("Excess bytes in TACK_Extension")

    @classmethod
    def createFromParameters(cls, tack, break_sigs, pin_activation):
        tackExtension                = cls()
        tackExtension.tack           = tack
        tackExtension.break_sigs     = break_sigs
        tackExtension.pin_activation = pin_activation

        return tackExtension

    def serialize(self):
        w = TlsStructureWriter(self._getSerializedLength())

        if self.tack:
            w.add(Tack.LENGTH, 1)
            w.add(self.tack.serialize(), Tack.LENGTH)
        else:
            w.add(0, 1)

        if self.break_sigs:
            w.add(len(self.break_sigs) * TackBreakSig.LENGTH, 2)
            for break_sig in self.break_sigs:
                w.add(break_sig.serialize(), TackBreakSig.LENGTH)
        else:
            w.add(0, 2)

        w.add(self.pin_activation, 1)

        assert(w.index == len(w.bytes)) # did we fill entire bytearray?
        return w.getBytes()

    def isEmpty(self):
        return not self.tack and not self.break_sigs

    def _getSerializedLength(self):
        length = 0
        if self.tack:
            length += Tack.LENGTH

        if self.break_sigs:
            length += len(self.break_sigs) * TackBreakSig.LENGTH

        return length + 4

    def _parseTack(self):
        tackLen = self.getInt(1)

        if tackLen != Tack.LENGTH:
            raise SyntaxError("TACK wrong size")

        return Tack(self.getBytes(tackLen))

    def _parseBreakSigs(self):
        sigsLen = self.getInt(2)

        if sigsLen > 1024:
            raise SyntaxError("break_sigs too large")
        elif sigsLen % TackBreakSig.LENGTH != 0:
            raise SyntaxError("break_sigs wrong size")

        break_sigs = []
        b2 = self.getBytes(sigsLen)
        while b2:
            break_sigs.append(TackBreakSig(b2[:TackBreakSig.LENGTH]))
            b2 = b2[TackBreakSig.LENGTH:]

        return break_sigs

    def __str__(self):
        result = ""

        if self.tack:
            result += str(self.tack)

        if self.break_sigs:
            for break_sig in self.break_sigs:
                result += str(break_sig)

        result += "pin_activation = %s\n" % TackActivation.STRINGS[self.pin_activation]

        return result
