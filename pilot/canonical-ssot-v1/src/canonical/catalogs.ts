export const REQUIRED_EVENT_KEYS = [
  "o_opp",
  "v_vdd",
  "i_idl",
  "q_qbr",
  "l_led",
  "k_kbi",
  "a_acc",
  "s_src",
  "e_e2e",
  "b_b2b",
  "n_n2c",
  "h_hor",
  "t_tzo",
  "d_dat"
] as const;

export const REQUIRED_IAM_KEYS = [
  "u_usr",
  "w_www",
  "m_mob",
  "c_con",
  "x_pwd",
  "f_hom",
  "z_zon"
] as const;

export const ROLE_CATALOG: Record<number, string> = {
  1: "admin-is-user",
  2: "super-is-guest",
  44: "supermario-is-sudo",
  51: "luigi-is-admin",
  63: "yoshi-is-manager",
  86: "isBrito"
};

export const ZONE_CATALOG: Record<number, string> = {
  254: "godBrito",
  1986: "sudoRoot",
  1999: "neo",
  2000: "y2k",
  2500: "staff",
  2666: "powerUser",
  2699: "editor",
  2700: "collaborator",
  2800: "audit",
  3000: "userManager",
  4000: "communityModerator",
  4500: "teamsModerator",
  5000: "editWriteRead",
  9900: "selfData",
  9950: "readContent",
  9980: "canLogin",
  9984: "resetPasswd",
  9985: "ssoOauth",
  9995: "canSignIn",
  9997: "viewPage",
  9998: "redirectHome",
  9999: "limitedView"
};

export type EventKey = (typeof REQUIRED_EVENT_KEYS)[number];
export type IAMKey = (typeof REQUIRED_IAM_KEYS)[number];
