# Stubs for Algorand clients — plug in your provider here.
# For real integration, use 'algosdk' for algod and a REST client for an indexer.
from typing import Any, Dict, List

class AlgodClientStub:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
    # add algod calls as you need

class IndexerClientStub:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token

    async def get_app_state(self, app_id: int) -> Dict[str, int]:
        # TODO: call your indexer to fetch global state (decode key/values)
        # Return keys: goal, rate, deadline, asa_id, raised, deposit, creator, admin
        return {}

    async def get_contributions(self, app_id: int) -> List[Dict[str, Any]]:
        # TODO: query indexer for payment tx to app address grouped with app call 'contribute'
        # Return list of {address, amount, txid, round}
        return []

    async def get_app_address(self, app_id: int) -> str:
        # TODO or compute from application ID (requires algod or formula); for now placeholder
        return ""
