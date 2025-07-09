%%{init: {
  "flowchart": {
    "nodeSpacing": 100,
    "rankSpacing": 400
  }
}}%%
flowchart TD
    N0["AMM.active_band"]
    N1["AMM.active_band_with_skip"]
    N2["AMM.can_skip_bands"]
    N3["AMM.deposit_range"]
    N4["AMM.get_rate_mul"]
    N5["AMM.get_sum_xy"]
    N6["AMM.get_x_down"]
    N7["AMM.p_oracle_up"]
    N8["AMM.price_oracle"]
    N9["AMM.read_user_tick_numbers"]
    N10["AMM.set_rate"]
    N11["AMM.withdraw"]
    N12["_calculate_debt_n1"]
    N13["_check_approval"]
    N14["_debt"]
    N15["_health"]
    N16["_log_2"]
    N17["_remove_from_list"]
    N18["_save_rate"]
    N19["get_y_effective"]
    N20["rate_write"]
    N21["repay"]
    N22["token.transferFrom"]
    N23["transferFrom"]
    N24["wad_ln"]
    N21 --> N14
    N21 --> N13
    N21 --> N11
    N21 --> N23
    N21 --> N17
    N21 --> N1
    N21 --> N9
    N21 --> N12
    N21 --> N3
    N21 --> N15
    N21 --> N18
    N14 --> N4
    N23 --> N22
    N12 --> N0
    N12 --> N7
    N12 --> N19
    N12 --> N24
    N12 --> N2
    N12 --> N8
    N24 --> N16
    N15 --> N6
    N15 --> N9
    N15 --> N8
    N15 --> N7
    N15 --> N5
    N15 --> N0
    N18 --> N20
    N18 --> N10
