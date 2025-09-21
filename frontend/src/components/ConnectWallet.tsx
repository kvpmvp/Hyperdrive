import { useWallet, Wallet, WalletId } from "@txnlab/use-wallet-react";

interface ConnectWalletProps {
  openModal: boolean;
  closeModal: () => void;
}

const ConnectWallet = ({ openModal, closeModal }: ConnectWalletProps) => {
  const { wallets, activeAddress } = useWallet();

  const isKmd = (wallet: Wallet) => wallet.id === WalletId.KMD;

  return (
    <dialog
      id="connect_wallet_modal"
      className={`modal ${openModal ? "modal-open" : ""}`}
    >
      <form method="dialog" className="modal-box">
        <h3 className="font-bold text-2xl">Select wallet provider</h3>

        <div className="grid m-2 pt-5">
          {activeAddress && (
            <>
              <p className="text-sm">Connected: {activeAddress}</p>
              <div className="divider" />
            </>
          )}

          {!activeAddress &&
            wallets?.map((wallet) => (
              <button
                className="btn border-teal-800 border-1 m-2"
                key={`provider-${wallet.id}`}
                onClick={(e) => {
                  e.preventDefault();
                  wallet.connect();
                }}
              >
                {!isKmd(wallet) && (
                  <img
                    alt={`wallet_icon_${wallet.id}`}
                    src={wallet.metadata.icon}
                    style={{ objectFit: "contain", width: "30px" }}
                  />
                )}
                <span>
                  {isKmd(wallet)
                    ? "LocalNet Wallet"
                    : wallet.metadata.name}
                </span>
              </button>
            ))}
        </div>

        <div className="modal-action ">
          <button
            className="btn"
            onClick={() => {
              closeModal();
            }}
          >
            Close
          </button>
          {activeAddress && (
            <button
              className="btn btn-warning"
              onClick={async () => {
                if (wallets) {
                  const activeWallet = wallets.find((w) => w.isActive);
                  if (activeWallet) {
                    await activeWallet.disconnect();
                  } else {
                    // required cleanup
                    localStorage.removeItem("@txnlab/use-wallet:v3");
                    window.location.reload();
                  }
                }
              }}
            >
              Logout
            </button>
          )}
        </div>
      </form>
    </dialog>
  );
};

export default ConnectWallet;
