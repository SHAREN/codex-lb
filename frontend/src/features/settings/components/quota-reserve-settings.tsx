import { useState } from "react";
import { Gauge } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { buildSettingsUpdateRequest } from "@/features/settings/payload";
import type { DashboardSettings, SettingsUpdateRequest } from "@/features/settings/schemas";

export type QuotaReserveSettingsProps = {
  settings: DashboardSettings;
  busy: boolean;
  onSave: (payload: SettingsUpdateRequest) => Promise<void>;
};

export function QuotaReserveSettings({ settings, busy, onSave }: QuotaReserveSettingsProps) {
  const [primaryReserve, setPrimaryReserve] = useState(String(settings.quotaReservePrimaryPercent));
  const [secondaryReserve, setSecondaryReserve] = useState(String(settings.quotaReserveSecondaryPercent));

  const save = (patch: Partial<SettingsUpdateRequest>) =>
    void onSave(buildSettingsUpdateRequest(settings, patch));

  const parsedPrimaryReserve = Number.parseFloat(primaryReserve);
  const primaryReserveValid = Number.isFinite(parsedPrimaryReserve) && parsedPrimaryReserve >= 0 && parsedPrimaryReserve <= 100;
  const primaryReserveChanged = primaryReserveValid && parsedPrimaryReserve !== settings.quotaReservePrimaryPercent;

  const parsedSecondaryReserve = Number.parseFloat(secondaryReserve);
  const secondaryReserveValid =
    Number.isFinite(parsedSecondaryReserve) && parsedSecondaryReserve >= 0 && parsedSecondaryReserve <= 100;
  const secondaryReserveChanged = secondaryReserveValid && parsedSecondaryReserve !== settings.quotaReserveSecondaryPercent;

  const reserveFieldsChanged = primaryReserveChanged || secondaryReserveChanged;
  const reserveFieldsValid = primaryReserveValid && secondaryReserveValid;

  return (
    <section className="rounded-xl border bg-card p-5">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
              <Gauge className="h-4 w-4 text-primary" aria-hidden="true" />
            </div>
            <div>
              <h3 className="text-sm font-semibold">Quota reserve</h3>
              <p className="text-xs text-muted-foreground">
                Stop routing to accounts when their remaining quota reaches this reserve.
              </p>
            </div>
          </div>
        </div>

        <div className="divide-y rounded-lg border">
          <div className="flex items-center justify-between p-3">
            <div>
              <p className="text-sm font-medium">Enable quota reserve</p>
              <p className="text-xs text-muted-foreground">Hold the final quota percentages instead of spending them.</p>
            </div>
            <Switch
              aria-label="Enable quota reserve"
              checked={settings.quotaReserveEnabled}
              disabled={busy}
              onCheckedChange={(checked) => save({ quotaReserveEnabled: checked })}
            />
          </div>

          <QuotaReservePercentRow
            label="Primary window reserve %"
            description="Reserve the last percent of the 5h or primary window."
            ariaLabel="Primary window reserve percent"
            value={primaryReserve}
            busy={busy}
            valid={primaryReserveValid}
            changed={primaryReserveChanged}
            onChange={setPrimaryReserve}
            onSave={() => save({ quotaReservePrimaryPercent: parsedPrimaryReserve })}
          />

          <QuotaReservePercentRow
            label="Secondary window reserve %"
            description="Reserve the last percent of the weekly or secondary window when one exists."
            ariaLabel="Secondary window reserve percent"
            value={secondaryReserve}
            busy={busy}
            valid={secondaryReserveValid}
            changed={secondaryReserveChanged}
            onChange={setSecondaryReserve}
            onSave={() => save({ quotaReserveSecondaryPercent: parsedSecondaryReserve })}
          />
        </div>

        <div className="flex justify-end">
          <Button
            type="button"
            size="sm"
            variant="outline"
            className="h-8 text-xs"
            disabled={busy || !reserveFieldsChanged || !reserveFieldsValid}
            onClick={() =>
              save({
                quotaReservePrimaryPercent: parsedPrimaryReserve,
                quotaReserveSecondaryPercent: parsedSecondaryReserve,
              })
            }
          >
            Save reserves
          </Button>
        </div>
      </div>
    </section>
  );
}

type QuotaReservePercentRowProps = {
  label: string;
  description: string;
  ariaLabel: string;
  value: string;
  busy: boolean;
  valid: boolean;
  changed: boolean;
  onChange: (value: string) => void;
  onSave: () => void;
};

function QuotaReservePercentRow({
  label,
  description,
  ariaLabel,
  value,
  busy,
  valid,
  changed,
  onChange,
  onSave,
}: QuotaReservePercentRowProps) {
  return (
    <div className="flex flex-col gap-3 p-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p className="text-sm font-medium">{label}</p>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
      <div className="flex items-center gap-2">
        <Input
          aria-label={ariaLabel}
          type="number"
          min={0}
          max={100}
          step={0.1}
          inputMode="decimal"
          value={value}
          disabled={busy}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && changed && valid) {
              onSave();
            }
          }}
          className="h-8 w-28 text-xs"
        />
        <Button
          type="button"
          size="sm"
          variant="outline"
          className="h-8 text-xs"
          disabled={busy || !changed || !valid}
          onClick={onSave}
        >
          Save
        </Button>
      </div>
    </div>
  );
}
