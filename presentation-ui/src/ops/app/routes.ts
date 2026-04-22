export const OPS_ROUTE_VALUES = [
  "workspaces",
  "connections",
  "models",
  "overview",
  "resources",
  "library",
  "chat",
  "actions",
  "scm",
] as const;

export type OpsRoute = (typeof OPS_ROUTE_VALUES)[number];
export type AppRoute = OpsRoute;

export const DEFAULT_OPS_ROUTE: OpsRoute = "overview";

export function normalizeOpsRoute(value: string | null | undefined): OpsRoute {
  return OPS_ROUTE_VALUES.includes(value as OpsRoute) ? (value as OpsRoute) : DEFAULT_OPS_ROUTE;
}
