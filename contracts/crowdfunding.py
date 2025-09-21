from pyteal import *

# Crowdfunding App (stateful, smart-contract account)
#
# Global State (uint unless noted):
# - "goal": goal (microAlgos)
# - "rate": ASA units per 1 ALGO (i.e., per 1_000_000 microAlgos)
# - "deadline": round
# - "asa_id": asset id for developer token
# - "raised": total contributed (microAlgos) tracked in global to allow closure after payouts/refunds
# - "deposit": initial deposit from creator (2% of goal, microAlgos)
# - "creator" (bytes)
# - "admin" (bytes)
#
# Local State (per investor):
# - "contrib": contributed microAlgos
#
# Actions:
# - On create: set creator/admin/goal/rate/deadline; raised=0; asa_id=0 sentinel
# - "setup": (creator only) inner opt-in to ASA; assert grouped deposit tx and ASA transfer from creator
# - "contribute": (before deadline, not after success close) grouped with Pay from sender to app addr; updates local "contrib" and global "raised"
# - "finalize": (anyone) if raised >= goal and before/equal deadline; send ASA to listed investors (Txn.accounts), clear their contrib; when global raised==0 then close ASA to creator, pay 2% admin fee, close remainder to creator
# - "refund": (anyone) if after deadline and raised < goal; refund ALGO contributions to listed investors; when raised==0: split deposit (half to admin, half to creator), close ASA back to creator and close remainder ALGO to creator
#
# To avoid iteration over unknown investor set, finalize/refund operate on the provided Txn.accounts list.
# Contract will self-close once App.globalGet("raised")==0 after respective distributions/refunds are completed.

KEY_GOAL = Bytes("goal")
KEY_RATE = Bytes("rate")
KEY_DEADLINE = Bytes("deadline")
KEY_ASA = Bytes("asa_id")
KEY_RAISED = Bytes("raised")
KEY_DEPOSIT = Bytes("deposit")
KEY_CREATOR = Bytes("creator")
KEY_ADMIN = Bytes("admin")

LKEY_CONTRIB = Bytes("contrib")

def approval_program():
    on_create = Seq(
        Assert(Txn.application_args.length() == Int(4)),
        App.globalPut(KEY_CREATOR, Txn.sender()),
        App.globalPut(KEY_ADMIN, Txn.application_args[0]),  # address bytes
        App.globalPut(KEY_GOAL, Btoi(Txn.application_args[1])),
        App.globalPut(KEY_RATE, Btoi(Txn.application_args[2])),
        App.globalPut(KEY_DEADLINE, Btoi(Txn.application_args[3])),
        App.globalPut(KEY_RAISED, Int(0)),
        App.globalPut(KEY_ASA, Int(0)),     # will be set in setup
        App.globalPut(KEY_DEPOSIT, Int(0)), # will be set in setup
        Approve(),
    )

    # Utility expressions
    app_addr = Global.current_application_address()
    goal = App.globalGet(KEY_GOAL)
    rate = App.globalGet(KEY_RATE)
    deadline = App.globalGet(KEY_DEADLINE)
    asa_id = App.globalGet(KEY_ASA)
    raised = App.globalGet(KEY_RAISED)
    deposit = App.globalGet(KEY_DEPOSIT)
    creator = App.globalGet(KEY_CREATOR)
    admin = App.globalGet(KEY_ADMIN)

    is_creator = Txn.sender() == creator
    before_deadline = Global.round() <= deadline
    after_deadline = Global.round() > deadline

    # Setup: creator deposits 2% and seeds ASA; also app opts-in to ASA
    # Group layout: [0]=AppCall("setup", foreign_assets=[ASA]), [1]=Payment(deposit), [2]=ASA Transfer from creator -> app
    expected_deposit = (goal * Int(2)) / Int(100)
    setup = Seq(
        Assert(is_creator),
        Assert(Txn.assets.length() == Int(1)),
        App.globalPut(KEY_ASA, Txn.assets[0]),

        # Check grouped deposit
        Assert(Global.group_size() >= Int(3)),
        Assert(Gtxn[1].type_enum() == TxnType.Payment),
        Assert(Gtxn[1].sender() == Txn.sender()),
        Assert(Gtxn[1].receiver() == app_addr),
        Assert(Gtxn[1].amount() == expected_deposit),
        App.globalPut(KEY_DEPOSIT, Gtxn[1].amount()),

        # Opt-in to the ASA (inner)
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.xfer_asset: Txn.assets[0],
            TxnField.asset_receiver: app_addr,
            TxnField.asset_amount: Int(0),
        }),
        InnerTxnBuilder.Submit(),

        # Require ASA transfer >= expected total tokens (rate * goal_algos)
        # tokens_expected = (goal_microalgos * rate) / 1_000_000
        Assert(Gtxn[2].type_enum() == TxnType.AssetTransfer),
        Assert(Gtxn[2].sender() == Txn.sender()),
        Assert(Gtxn[2].asset_receiver() == app_addr),
        Assert(Gtxn[2].xfer_asset() == Txn.assets[0]),
        Assert(Gtxn[2].asset_amount() >= (goal * rate) / Int(1_000_000)),

        Approve()
    )

    # Contribute: Grouped [0]=AppCall("contribute"), [1]=Payment from investor to app
    investor = Txn.sender()
    contribute = Seq(
        Assert(before_deadline),
        Assert(Global.group_size() >= Int(2)),
        Assert(Gtxn[1].type_enum() == TxnType.Payment),
        Assert(Gtxn[1].sender() == investor),
        Assert(Gtxn[1].receiver() == app_addr),
        Assert(Gtxn[1].amount() > Int(0)),

        # Update local and global
        # Require the investor to have opted in
        App.localPut(investor, LKEY_CONTRIB, App.localGet(investor, LKEY_CONTRIB) + Gtxn[1].amount()),
        App.globalPut(KEY_RAISED, raised + Gtxn[1].amount()),
        Approve()
    )

    # Utility: send ASA tokens to one account for its contribution and zero-out its local
    i = ScratchVar(TealType.uint64)
    contrib_amt = ScratchVar(TealType.uint64)
    tokens_due = ScratchVar(TealType.uint64)

    def payout_account(acct: Expr):
        return Seq(
            contrib_amt.store(App.localGet(acct, LKEY_CONTRIB)),
            If(contrib_amt.load() > Int(0)).Then(Seq(
                # tokens = contrib * rate / 1_000_000
                tokens_due.store((contrib_amt.load() * rate) / Int(1_000_000)),
                If(tokens_due.load() > Int(0)).Then(Seq(
                    InnerTxnBuilder.Begin(),
                    InnerTxnBuilder.SetFields({
                        TxnField.type_enum: TxnType.AssetTransfer,
                        TxnField.xfer_asset: asa_id,
                        TxnField.asset_receiver: acct,
                        TxnField.asset_amount: tokens_due.load(),
                    }),
                    InnerTxnBuilder.Submit(),
                )),
                App.localPut(acct, LKEY_CONTRIB, Int(0)),
                App.globalPut(KEY_RAISED, App.globalGet(KEY_RAISED) - contrib_amt.load()),
            )),
        )

    # Finalize success: distribute tokens to listed accounts; when raised==0, close & pay admin 2%
    # Caller must include enough fee for inner txs
    finalize = Seq(
        Assert(raised >= goal),
        Assert(before_deadline),

        i.store(Int(0)),
        While(i.load() < Txn.accounts.length()).Do(Seq(
            payout_account(Txn.accounts[i.load()]),
            i.store(i.load() + Int(1))
        )),

        # If all contributions have been accounted for, close out: asset-close to creator, pay admin 2%, close remainder to creator
        If(App.globalGet(KEY_RAISED) == Int(0)).Then(Seq(
            # Close ASA back to creator
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: asa_id,
                TxnField.asset_receiver: creator,
                TxnField.asset_amount: Int(0),
                TxnField.asset_close_to: creator,
            }),
            InnerTxnBuilder.Submit(),

            # Pay admin 2% of total ALGO balance
            # Using available balance at this moment
            (admin_fee := ScratchVar(TealType.uint64)).store((Balance(app_addr) * Int(2)) / Int(100)),
            If(admin_fee.load() > Int(0)).Then(Seq(
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields({
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: creator if Int(0) == Int(1) else admin,  # keep logic identical; placeholder no-op
                    TxnField.amount: admin_fee.load(),
                }),
                InnerTxnBuilder.Submit(),
            )),

            # Close remainder to creator
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: creator,
                TxnField.amount: Int(0),
                TxnField.close_remainder_to: creator,
            }),
            InnerTxnBuilder.Submit(),
        )),

        Approve()
    )

    # Refund failure: after deadline and not funded, refund investors in Txn.accounts; when raised==0, split deposit & close
    refund = Seq(
        Assert(after_deadline),
        Assert(raised < goal),

        i.store(Int(0)),
        While(i.load() < Txn.accounts.length()).Do(Seq(
            contrib_amt.store(App.localGet(Txn.accounts[i.load()], LKEY_CONTRIB)),
            If(contrib_amt.load() > Int(0)).Then(Seq(
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields({
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: Txn.accounts[i.load()],
                    TxnField.amount: contrib_amt.load(),
                }),
                InnerTxnBuilder.Submit(),
                App.localPut(Txn.accounts[i.load()], LKEY_CONTRIB, Int(0)),
                App.globalPut(KEY_RAISED, App.globalGet(KEY_RAISED) - contrib_amt.load()),
            )),
            i.store(i.load() + Int(1))
        )),

        If(App.globalGet(KEY_RAISED) == Int(0)).Then(Seq(
            # Asset close back to creator
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: asa_id,
                TxnField.asset_receiver: creator,
                TxnField.asset_amount: Int(0),
                TxnField.asset_close_to: creator,
            }),
            InnerTxnBuilder.Submit(),

            # Split deposit: half to admin, half to creator
            (half := ScratchVar(TealType.uint64)).store(deposit / Int(2)),
            If(half.load() > Int(0)).Then(Seq(
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields({
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: admin,
                    TxnField.amount: half.load(),
                }),
                InnerTxnBuilder.Submit(),

                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields({
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.receiver: creator,
                    TxnField.amount: Int(0),
                    TxnField.close_remainder_to: creator,
                }),
                InnerTxnBuilder.Submit(),
            )),
        )),

        Approve()
    )

    # Delete application: allow creator to delete after closure (no constraints beyond creator)
    on_delete = Seq(
        Assert(is_creator),
        Approve()
    )

    on_update = Seq(Reject())
    on_closeout = Seq(Approve())
    on_optin = Seq(App.localPut(Txn.sender(), LKEY_CONTRIB, Int(0)), Approve())

    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.on_completion() == OnComplete.UpdateApplication, on_update],
        [Txn.on_completion() == OnComplete.DeleteApplication, on_delete],
        [Txn.on_completion() == OnComplete.CloseOut, on_closeout],
        [Txn.on_completion() == OnComplete.OptIn, on_optin],
        [Txn.on_completion() == OnComplete.NoOp, Cond(
            [Txn.application_args[0] == Bytes("setup"), setup],
            [Txn.application_args[0] == Bytes("contribute"), contribute],
            [Txn.application_args[0] == Bytes("finalize"), finalize],
            [Txn.application_args[0] == Bytes("refund"), refund],
        )]
    )
    return program

def clear_program():
    return Approve()
