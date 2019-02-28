import pytest

from eth_utils import (
    ValidationError,
)

from eth2.beacon.state_machines.forks.serenity.block_validation import (
    validate_proposer_slashing,
    validate_proposer_slashing_block_root,
    validate_proposer_slashing_is_slashed,
    validate_proposer_slashing_slot,
    validate_proposer_slashing_shard,
    validate_proposal_signature,
)
from eth2.beacon.tools.builder.validator import (
    create_mock_proposer_slashing_at_block,
)


def get_valid_proposer_slashing(state,
                                keymap,
                                config,
                                proposer_index=0):
    return create_mock_proposer_slashing_at_block(
        state,
        config,
        keymap,
        block_root_1=b'\x11' * 32,
        block_root_2=b'\x22' * 32,
        proposer_index=proposer_index,
    )


def test_validate_proposer_slashing_valid(genesis_state,
                                          keymap,
                                          slots_per_epoch,
                                          config):
    state = genesis_state
    valid_proposer_slashing = get_valid_proposer_slashing(
        state,
        keymap,
        config,
    )
    validate_proposer_slashing(state, valid_proposer_slashing, slots_per_epoch)


def test_validate_proposer_slashing_slot(genesis_state,
                                         keymap,
                                         config):
    state = genesis_state
    valid_proposer_slashing = get_valid_proposer_slashing(
        state,
        keymap,
        config,
    )
    # Valid
    validate_proposer_slashing_slot(valid_proposer_slashing)

    proposal_data_1 = valid_proposer_slashing.proposal_data_1.copy(
        slot=valid_proposer_slashing.proposal_data_2.slot + 1
    )
    invalid_proposer_slashing = valid_proposer_slashing.copy(
        proposal_data_1=proposal_data_1,
    )

    # Invalid
    with pytest.raises(ValidationError):
        validate_proposer_slashing_slot(invalid_proposer_slashing)


def test_validate_proposer_slashing_shard(genesis_state,
                                          keymap,
                                          config):
    state = genesis_state
    valid_proposer_slashing = get_valid_proposer_slashing(
        state,
        keymap,
        config,
    )

    # Valid
    validate_proposer_slashing_shard(valid_proposer_slashing)

    proposal_data_1 = valid_proposer_slashing.proposal_data_1.copy(
        shard=valid_proposer_slashing.proposal_data_2.shard + 1
    )
    invalid_proposer_slashing = valid_proposer_slashing.copy(
        proposal_data_1=proposal_data_1,
    )

    # Invalid
    with pytest.raises(ValidationError):
        validate_proposer_slashing_shard(invalid_proposer_slashing)


def test_validate_proposer_slashing_block_root(genesis_state,
                                               keymap,
                                               config):
    state = genesis_state
    valid_proposer_slashing = get_valid_proposer_slashing(
        state,
        keymap,
        config,
    )

    # Valid
    validate_proposer_slashing_block_root(valid_proposer_slashing)

    proposal_data_1 = valid_proposer_slashing.proposal_data_1.copy(
        block_root=valid_proposer_slashing.proposal_data_2.block_root
    )
    invalid_proposer_slashing = valid_proposer_slashing.copy(
        proposal_data_1=proposal_data_1,
    )

    # Invalid
    with pytest.raises(ValidationError):
        validate_proposer_slashing_block_root(invalid_proposer_slashing)


@pytest.mark.parametrize(
    (
        'slashed', 'success'
    ),
    [
        (False, True),
        (True, False),
    ],
)
def test_validate_proposer_slashing_is_slashed(slots_per_epoch,
                                               genesis_state,
                                               beacon_chain_shard_number,
                                               keymap,
                                               slashed,
                                               success):
    # Invalid
    if success:
        validate_proposer_slashing_is_slashed(slashed)
    else:
        with pytest.raises(ValidationError):
            validate_proposer_slashing_is_slashed(slashed)


def test_validate_proposal_signature(slots_per_epoch,
                                     genesis_state,
                                     keymap,
                                     config):
    state = genesis_state
    proposer_index = 0
    valid_proposer_slashing = get_valid_proposer_slashing(
        state,
        keymap,
        config,
    )
    proposer = state.validator_registry[proposer_index]

    # Valid
    validate_proposal_signature(
        proposal_signed_data=valid_proposer_slashing.proposal_data_1,
        proposal_signature=valid_proposer_slashing.proposal_signature_1,
        pubkey=proposer.pubkey,
        fork=state.fork,
        slots_per_epoch=slots_per_epoch,
    )

    # Invalid
    wrong_proposer_index = proposer_index + 1
    wrong_proposer = state.validator_registry[wrong_proposer_index]
    with pytest.raises(ValidationError):
        validate_proposal_signature(
            proposal_signed_data=valid_proposer_slashing.proposal_data_1,
            proposal_signature=valid_proposer_slashing.proposal_signature_1,
            pubkey=wrong_proposer.pubkey,
            fork=state.fork,
            slots_per_epoch=slots_per_epoch,
        )