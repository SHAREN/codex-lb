import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { QuotaReserveSettings } from "@/features/settings/components/quota-reserve-settings";
import { createDashboardSettings } from "@/test/mocks/factories";

describe("QuotaReserveSettings", () => {
  it("saves quota reserve toggle and percentages", async () => {
    const user = userEvent.setup();
    const onSave = vi.fn().mockResolvedValue(undefined);
    const settings = createDashboardSettings({
      quotaReserveEnabled: false,
      quotaReservePrimaryPercent: 0,
      quotaReserveSecondaryPercent: 0,
    });

    render(<QuotaReserveSettings settings={settings} busy={false} onSave={onSave} />);

    await user.click(screen.getByRole("switch", { name: "Enable quota reserve" }));

    expect(onSave).toHaveBeenCalledWith(
      expect.objectContaining({
        quotaReserveEnabled: true,
        quotaReservePrimaryPercent: 0,
        quotaReserveSecondaryPercent: 0,
      }),
    );

    await user.clear(screen.getByRole("spinbutton", { name: "Primary window reserve percent" }));
    await user.type(screen.getByRole("spinbutton", { name: "Primary window reserve percent" }), "3");
    await user.clear(screen.getByRole("spinbutton", { name: "Secondary window reserve percent" }));
    await user.type(screen.getByRole("spinbutton", { name: "Secondary window reserve percent" }), "1");
    await user.click(screen.getByRole("button", { name: "Save reserves" }));

    expect(onSave).toHaveBeenLastCalledWith(
      expect.objectContaining({
        quotaReservePrimaryPercent: 3,
        quotaReserveSecondaryPercent: 1,
      }),
    );
  });

  it("does not save invalid reserve percentages", async () => {
    const user = userEvent.setup();
    const onSave = vi.fn().mockResolvedValue(undefined);
    const settings = createDashboardSettings({ quotaReservePrimaryPercent: 3 });

    render(<QuotaReserveSettings settings={settings} busy={false} onSave={onSave} />);

    await user.clear(screen.getByRole("spinbutton", { name: "Primary window reserve percent" }));
    await user.type(screen.getByRole("spinbutton", { name: "Primary window reserve percent" }), "101");

    expect(screen.getByRole("button", { name: "Save reserves" })).toBeDisabled();
  });
});
