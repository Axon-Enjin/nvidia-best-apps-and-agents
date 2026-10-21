// Wire types for the FastAPI review service. Field names and nullability follow
// the Python response builders; server enums stay `string` so an unknown value
// renders generically instead of breaking the page.

export type Actor = {
  id: string | null;
  username: string;
  roles: string[];
};

export type SessionState = {
  authenticated: boolean;
  protected: boolean;
  auth_mode: string;
  actor: Actor | null;
  csrf_token: string | null;
};
