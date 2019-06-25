from eth_typing import (
    BLSSignature,
)
import ssz
from ssz.sedes import (
    bytes96,
    uint64,
)

from eth2.beacon.typing import (
    Epoch,
    ValidatorIndex,
)
from eth2.beacon.constants import EMPTY_SIGNATURE


class VoluntaryExit(ssz.SignedSerializable):

    fields = [
        # Minimum epoch for processing exit
        ('epoch', uint64),
        ('validator_index', uint64),
        ('signature', bytes96),
    ]

    def __init__(self,
                 epoch: Epoch=Epoch(0),
                 validator_index: ValidatorIndex=ValidatorIndex(0),
                 signature: BLSSignature=EMPTY_SIGNATURE) -> None:
        super().__init__(
            epoch,
            validator_index,
            signature,
        )
