import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { AuthProvider } from "./lib/auth";

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = typeof input === "string" ? input : input.toString();
        if (url.includes("/api/v1/auth/me")) {
          return new Response(JSON.stringify({ detail: "Unauthorized" }), {
            status: 401,
            headers: { "Content-Type": "application/json" }
          });
        }
        throw new Error(`Unexpected request in test: ${url}`);
      })
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("should render login page by default", async () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={["/"]}>
          <App />
        </MemoryRouter>
      </AuthProvider>
    );

    expect(await screen.findByText("企业 SSO 登录")).toBeInTheDocument();
  });
});
