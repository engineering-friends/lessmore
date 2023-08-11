import os

from typing import Any, Optional, Union

import grpc


def _read_file_or_encode(value: Optional[Union[str, bytes]]):
    if value is None:
        return None
    elif isinstance(value, str):
        if os.path.exists(value):
            with open(value, "rb") as f:
                return f.read()
        else:
            return value.encode()
    elif isinstance(value, bytes):
        return value
    else:
        raise ValueError(f"Unexpected value type: {type(value)}")


class GRPCClient:
    """Simple helper to make methods of GRPC stubs easier to use"""

    def __init__(
        self,
        host: str,
        access_token: Optional[str] = None,
        root_certificates: Optional[str] = None,
        certificate_chain: Optional[str] = None,
        private_key: Optional[str] = None,
        ssl: bool = True,
    ):
        self.host = host
        self.access_token = access_token
        self.ssl = ssl

        self.certificate_chain = _read_file_or_encode(certificate_chain)
        self.private_key = _read_file_or_encode(private_key)
        self.root_certificates = _read_file_or_encode(root_certificates)

        self._channel = None

    def _get_channel(self) -> grpc.Channel:
        if self._channel is None:
            if self.ssl:
                # - Prepare credentials

                credentials_list = [
                    grpc.ssl_channel_credentials(
                        root_certificates=self.root_certificates,
                        certificate_chain=self.certificate_chain,
                        private_key=self.private_key,
                    )
                ]
                if self.access_token:
                    credentials_list.append(grpc.access_token_call_credentials(self.access_token))

                if len(credentials_list) == 1:
                    credentials = credentials_list[0]
                else:
                    credentials = grpc.composite_channel_credentials(*credentials_list)

                # - Create secure channel

                self._channel = grpc.secure_channel(
                    target=self.host,
                    credentials=credentials,
                )
            else:
                self._channel = grpc.insecure_channel(target=self.host)

        return self._channel

    def make_grpc_request(
        self,
        stub_class: Any,
        request: Any,
        method: str,
        timeout: int = 5,  # seconds
    ) -> Any:
        # - Prepare kwargs

        kwargs = {}
        if not self.ssl and self.access_token:
            kwargs["metadata"] = [("authorization", f"Bearer {self.access_token}")]

        # - Make get request

        return getattr(stub_class(self._get_channel()), method)(request=request, timeout=timeout, **kwargs)


def test():
    # todo: make independent test from colluder-gun

    from deeplay.schemas.proto.build.deeplay.ultron.replay_urls.v1 import replay_urls_pb2, replay_urls_pb2_grpc
    from pyflink_etl.pipelines.colluder_gun.config.colluder_gun_config import colluder_gun_config

    grpc_client = GRPCClient(
        host=colluder_gun_config.hhpoker_replayer_grpc_host,
        root_certificates=colluder_gun_config.hhpoker_replayer_grpc_root_certificates,
        private_key=colluder_gun_config.hhpoker_replayer_grpc_private_key,
        certificate_chain=colluder_gun_config.hhpoker_replayer_grpc_certificate_chain,
    )

    print(
        grpc_client.make_grpc_request(
            stub_class=replay_urls_pb2_grpc.ReplayURLsStub,
            request=replay_urls_pb2.GetReplayURLRequest(
                room_id="PMTR",
                account_id="118235039",
                table_id="94537040",
                hand_id="94537040-105",
            ),
            timeout=120,
            method="GetReplayURL",
        ).url
    )


if __name__ == "__main__":
    test()
