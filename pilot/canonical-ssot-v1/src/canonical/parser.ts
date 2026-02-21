import { REQUIRED_EVENT_KEYS, REQUIRED_IAM_KEYS, ROLE_CATALOG, ZONE_CATALOG, type EventKey, type IAMKey } from "./catalogs";
import { CanonicalError } from "./errors";
import type { RawCanonicalRecord } from "./types";

const LINE_REGEX = /^\s*\[([a-z]_[a-z0-9]+)]\s*:\s*(.*?)\s*(?:#.*)?$/i;

const KEY_SET = new Set([...REQUIRED_EVENT_KEYS, ...REQUIRED_IAM_KEYS]);

function assertRegex(key: string, value: string, pattern: RegExp, message: string): void {
  if (!pattern.test(value)) {
    throw new CanonicalError("E_PARSE_FORMAT", message, { key, value, pattern: pattern.source });
  }
}

function parsePrefixedCode(value: string, prefix: string): number {
  const match = value.match(new RegExp(`^${prefix}_(\\d+)-`));
  if (!match) {
    throw new CanonicalError("E_IAM_FORMAT", `Expected prefix ${prefix}_<num>-`, { value });
  }
  return Number(match[1]);
}

function validateValueFormats(record: RawCanonicalRecord): void {
  if (record.i_idl !== "i_q-l-k-a-s-e-b-n-h-t-d") {
    throw new CanonicalError("E_PARSE_INVARIANT", "i_idl must be i_q-l-k-a-s-e-b-n-h-t-d", {
      key: "i_idl",
      value: record.i_idl
    });
  }

  assertRegex("k_kbi", record.k_kbi, /^k_\d{8}-\d{6}$/, "k_kbi must match k_yyyyMMdd-HHmmss");
  assertRegex("h_hor", record.h_hor, /^h_\d{2}-\d{2}-\d{2}$/, "h_hor must match h_HH-mm-ss");
  assertRegex("d_dat", record.d_dat, /^d_\d{2}-\d{2}-\d{2}$/, "d_dat must match d_dd-MM-yy");
  assertRegex("t_tzo", record.t_tzo, /^t_\d+-[A-Za-z_]+\/[A-Za-z_]+$/, "t_tzo must match t_<num>-Area/City");
  assertRegex("u_usr", record.u_usr, /^u_\d+-\$\{a_\*-\}-[A-Za-z0-9_-]+$/, "u_usr must include ${a_*-}");
  assertRegex("w_www", record.w_www, /^w_[a-z0-9-]+$/, "w_www must match w_<domain-with-dashes>");
  assertRegex("m_mob", record.m_mob, /^m_\d{8,16}$/, "m_mob must have numeric digits only");
  assertRegex("f_hom", record.f_hom, /^f_home-\$\{u_\d+}$/, "f_hom must match f_home-${u_<code>}");
  assertRegex("z_zon", record.z_zon, /^z_\d+-c_\d+-u_\d+$/, "z_zon must match z_<level>-c_<code>-u_<code>");

  const passwordMatch = record.x_pwd.match(/^x_(\d+)-(.+)$/);
  if (!passwordMatch) {
    throw new CanonicalError("E_PARSE_FORMAT", "x_pwd must match x_<min>-<secret>", { key: "x_pwd" });
  }
  const min = Number(passwordMatch[1]);
  const secret = passwordMatch[2];
  if (secret.length < min) {
    throw new CanonicalError("E_PARSE_FORMAT", "x_pwd secret must have length >= min", {
      key: "x_pwd",
      min,
      current: secret.length
    });
  }

  const roleCode = parsePrefixedCode(record.c_con, "c");
  if (!ROLE_CATALOG[roleCode]) {
    throw new CanonicalError("E_IAM_ROLE", "c_con role code not found in catalog", {
      key: "c_con",
      roleCode
    });
  }

  const zoneMatch = record.z_zon.match(/^z_(\d+)-c_(\d+)-u_(\d+)$/);
  if (!zoneMatch) {
    throw new CanonicalError("E_IAM_FORMAT", "z_zon format is invalid", { key: "z_zon" });
  }
  const zoneLevel = Number(zoneMatch[1]);
  const cCodeInZone = Number(zoneMatch[2]);

  if (!ZONE_CATALOG[zoneLevel]) {
    throw new CanonicalError("E_IAM_ZONE", "z_zon zone code not found in catalog", {
      key: "z_zon",
      zoneLevel
    });
  }

  if (cCodeInZone !== roleCode) {
    throw new CanonicalError("E_IAM_INCONSISTENCY", "c_con code must match z_zon embedded c_<code>", {
      c_con: roleCode,
      z_zon: cCodeInZone
    });
  }

  if (!record.u_usr.includes("${a_*-}")) {
    throw new CanonicalError("E_PARSE_REFERENCE", "u_usr must include account reference ${a_*-}", {
      key: "u_usr"
    });
  }

  if (!record.a_acc) {
    throw new CanonicalError("E_PARSE_REFERENCE", "a_acc is required to resolve user reference", {
      key: "a_acc"
    });
  }
}

export function parseCanonicalDsl(input: string): RawCanonicalRecord {
  const output = {} as RawCanonicalRecord;
  const seen = new Set<string>();

  const lines = input.split(/\r?\n/);

  for (let index = 0; index < lines.length; index += 1) {
    const raw = lines[index].trim();
    if (!raw || raw.startsWith("#") || raw.startsWith("---")) {
      continue;
    }

    const match = lines[index].match(LINE_REGEX);
    if (!match) {
      throw new CanonicalError("E_PARSE_SYNTAX", "Invalid DSL line", {
        line: index + 1,
        raw: lines[index]
      });
    }

    const [, key, value] = match;
    if (!KEY_SET.has(key as EventKey | IAMKey)) {
      throw new CanonicalError("E_PARSE_KEY", "Unknown canonical key", { key, line: index + 1 });
    }
    if (seen.has(key)) {
      throw new CanonicalError("E_PARSE_DUPLICATE", "Duplicated canonical key", { key, line: index + 1 });
    }
    seen.add(key);
    output[key as EventKey | IAMKey] = value;
  }

  const missingEvent = REQUIRED_EVENT_KEYS.filter((key) => !(key in output));
  if (missingEvent.length > 0) {
    throw new CanonicalError("E_PARSE_MISSING_EVENT", "Missing event layer keys", { keys: missingEvent });
  }

  const missingIAM = REQUIRED_IAM_KEYS.filter((key) => !(key in output));
  if (missingIAM.length > 0) {
    throw new CanonicalError("E_PARSE_MISSING_IAM", "Missing IAM layer keys", { keys: missingIAM });
  }

  validateValueFormats(output);

  return output;
}

export function extractRoleCode(cCon: string): number {
  return parsePrefixedCode(cCon, "c");
}

export function extractZoneLevel(zZon: string): number {
  const match = zZon.match(/^z_(\d+)-/);
  if (!match) {
    throw new CanonicalError("E_IAM_FORMAT", "z_zon format is invalid", { value: zZon });
  }
  return Number(match[1]);
}
