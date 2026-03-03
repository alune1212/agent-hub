import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import App from "./App";
import { AuthProvider } from "./lib/auth";

describe("App", () => {
  it("should render dashboard title", () => {
    render(
      <AuthProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </AuthProvider>
    );

    expect(screen.getByText("管理与审计系统")).toBeInTheDocument();
  });
});
