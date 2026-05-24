# Travel Planning — Working Notes

> Living document. Captures the user's thinking for a personalized travel-
> planning skill. Status: **collecting requirements** — convert to a SKILL.md
> (+ references) later. The user will keep adding thinking; append to the
> relevant section and log it under "Change log".

## Goal

Save time on travel research and surface the best solution right away, tailored
to the user's personal preferences across different travel scenarios. Not a
generic planner — it should encode *this user's* criteria so it can make
recommendations quickly instead of re-researching from scratch each time.

## Overall workflow (end-to-end trip)

Default sequence for a trip:

1. **Research flights** → pick best option.
2. **Book flight tickets.**
3. **Book lodging** (hotel vs Airbnb decision — see criteria).
4. **Book trains** if the trip includes other cities/destinations.

Example scenario used to develop this: **London trip** (multi-city potential →
flight + hotel + intercity train).

## Decision criteria by stage

### 1. Flights

- _(Details to come from user.)_
- Known preference from prior context: **2 adults** and **direct flights only**
  for award/reward-seat research. _(Confirm whether this applies to all flight
  research or only award bookings.)_
- Possible integration: existing `va-reward-search` skill already sweeps Virgin
  Atlantic award availability — the travel skill may call/borrow from it for
  points bookings. _(Decide relationship later.)_

### 2. Lodging — hotel vs Airbnb

Open question to resolve per trip: **book a hotel or an Airbnb?**
- The user has **evaluation criteria for hotel-vs-Airbnb to share later** —
  _(placeholder; capture when provided.)_

Whatever the lodging type, evaluate on:

- **Location quality** — "good location" means:
  - Close to a subway/metro station.
  - Close to all the places the user wants to visit on the trip.
  - Close to **Chinese restaurants**.
  - Close to **convenience stores**.
- **Rating** — must be well-rated.
- **Noise** — must be quiet; the user is a **light sleeper**, so low-noise
  rooms/locations are important (avoid busy streets, nightlife, near
  elevators/AC, etc.).

### 3. Intercity trains

- Needed when the trip extends to other cities (e.g., from London to elsewhere).
- _(Criteria/preferences to come from user.)_

## Open items / to capture from user

- [ ] Flight selection criteria (airlines, cabin, layover tolerance, price vs
      points, timing, airports).
- [ ] Hotel-vs-Airbnb evaluation criteria (user said they'll share).
- [ ] Definition of "close" (walking minutes? distance?) for location scoring.
- [ ] Train preferences (class, operator, advance booking, rail passes).
- [ ] Budget approach and trade-off priorities (cost vs convenience vs comfort).
- [ ] Trip-type variations (solo vs with partner, work vs leisure, city vs
      multi-city) and how criteria change.
- [ ] Output format the user wants (ranked options? a booking checklist? links?).

## Change log

- Initial capture: goal, end-to-end workflow, London example, flight note
  (2 adults / direct), lodging location+rating+noise criteria, hotel-vs-Airbnb
  placeholder, train placeholder, open items.
