import numpy as np

from synth.audio import ChannelRouter, OutputChannel


class TestChannelRouter:
    def test_left_channel_mutes_right(self) -> None:
        mono = np.array([0.1, -0.2], dtype=np.float32)

        stereo = ChannelRouter().route(mono, OutputChannel.LEFT)

        assert stereo.shape == (2, 2)
        assert np.allclose(stereo[:, 0], mono)
        assert np.allclose(stereo[:, 1], 0.0)

