# Gaming & Game Dev — Gap-Fill Wave

**Current catalog:** 336 repos across 28 subdomains
**Target after gap-fill:** 550-650 repos
**Strategy:** Focus on the 15 thinnest subdomains (3-12 repos each) with known missing repos from initial research

---

## Priority Tiers

### Tier 1: Critical Gaps (under 10 repos, research identified 2-3x more)

#### 1. `game-server-orchestration` — 3 repos → target 15+
**Missing:**
- Agones (googleforgames/agones, 6.7k) — Kubernetes game server hosting
- Open Match (googleforgames/open-match, 3.4k) — matchmaking framework
- Open Saves (googleforgames/open-saves) — cloud-native game data store
- Quilkin (googleforgames/quilkin) — UDP proxy for game servers
- Rivet (rivet-gg/rivet) — open-source game server management
- AccelByte matchmaking tools
- Edgegap/lobby systems
- Rating/ranking libraries (Elo, Glicko-2, TrueSkill implementations)

**Search queries:**
- "game server kubernetes open source"
- "matchmaking algorithm github"
- "elo rating system library"
- "game lobby system open source"
- "dedicated game server scaling"

---

#### 2. `visual-novel-engines` — 7 repos → target 20+
**Missing:**
- Twine (klembot/twinejs, ~4k) — interactive fiction
- Dialogic (dialogic-godot/dialogic) — Godot dialogue addon
- NaniNovel (naninovel) — Unity visual novel engine
- Ink runtime ports (inkle/ink-unity-integration, ink-js)
- Fungus (snozbot/fungus) — Unity storytelling framework
- Katawa Shoujo engine derivatives
- Open-source visual novel games with reusable engines (Doki Doki Mod Template)
- Card/board game engines (boardgame.io, Cardshifter)

**Search queries:**
- "visual novel engine github"
- "twine interactive fiction"
- "dialogic godot"
- "fungus unity storytelling"
- "interactive fiction tool open source"

---

#### 3. `modding-frameworks` — 7 repos → target 18+
**Missing:**
- MelonLoader (LavaGang/MelonLoader) — already in catalog, check others
- SMAPI (Pathoschild/SMAPI) — Stardew Valley modding API
- Harmony (pardeike/Harmony, 5k) — .NET runtime patching
- Oxide/uMod — Rust/Unity game modding framework
- Thunderstore mod manager
- r2modman mod manager
- Godot mod loader
- MonoMod — .NET assembly manipulation

**Search queries:**
- "game mod loader open source"
- "harmony patching .net"
- "unity modding framework"
- "godot mod loader"
- "runtime patching game"

---

#### 4. `asset-tools` — 7 repos → target 20+
**Missing:**
- Tiled (mapeditor/tiled, 11k) — the standard tilemap editor
- LDtk (deepnight/ldtk, 3.5k) — modern level editor by Dead Cells dev
- TrenchBroom (TrenchBroom/TrenchBroom, 2k) — BSP level editor
- Goxel (guillaumechereau/goxel, 2.7k) — open-source voxel editor
- Aseprite (aseprite/aseprite, 30k) — pixel art tool (source available)
- Pixelorama (Orama-Interactive/Pixelorama) — Godot-made pixel art editor
- Material Maker (RodZill4/material-maker) — procedural material editor
- ArmorPaint — open-source 3D texture painting
- GodotSteam, Gamemaker-like tools

**Search queries:**
- "level editor open source 2026"
- "pixel art editor github"
- "voxel editor open source"
- "tilemap editor game"
- "procedural material editor"
- "3d texture painting open source"

---

#### 5. `game-audio` — 8 repos → target 20+
**Missing:**
- miniaudio (mackron/miniaudio, 6.5k) — single-file audio library
- OpenAL Soft (kcat/openal-soft, 2.6k) — 3D audio API
- Steam Audio (ValveSoftware/steam-audio, 2.8k) — physics-based propagation
- dr_libs (mackron/dr_libs, 1.7k) — single-file audio decoders
- Kira (tesselode/kira, 1k) — Rust expressive game audio
- Rodio (RustAudio/rodio, 2.3k) — Rust audio playback
- CPAL (RustAudio/cpal, 3.6k) — cross-platform audio I/O
- Google Pindrop — game audio library
- Resonance Audio (resonance-audio/resonance-audio) — spatial audio SDK

**Search queries:**
- "game audio library C++"
- "spatial audio library open source"
- "rust audio game library"
- "audio decoder single header"
- "web audio game engine"

---

#### 6. `game-scripting` — 8 repos → target 20+
**Missing:**
- Luau (luau-lang/luau, 5k) — Roblox's typed Lua
- sol2/sol3 (ThePhD/sol2, 4.9k) — C++ Lua binding
- AngelScript — game scripting language
- LuaBridge3 (kunitoki/LuaBridge3) — lightweight Lua binding
- Squirrel (albertodemichelis/squirrel) — embedded scripting
- Gravity (marcobambini/gravity) — Swift-like embedded language
- Dyon — Rust scripting language
- mun-lang/mun — hot-reloading scripting
- Luau, LuaJIT bindings for various engines

**Search queries:**
- "embeddable scripting language github"
- "lua binding C++ game"
- "luau scripting language"
- "angelscript game scripting"
- "squirrel scripting language"

---

#### 7. `ecs-frameworks` — 8 repos → target 22+
**Missing:**
- Bevy ECS standalone usage docs
- legion (amethyst/legion, 1.7k)
- hecs (Ralith/hecs, 1.2k)
- Arch (genaray/Arch, 1.6k) — C# high-perf ECS
- DefaultEcs — .NET ECS
- ECSY (ecsyjs/ecsy, 1.1k) — web ECS
- bitECS (NateTheGreatt/bitECS, 1.2k)
- Shipyard — Rust sparse-set ECS
- EntityX (alecthomas/entityx, 2.3k)
- DOD resource lists (dbartolini/data-oriented-design, 2k)

**Search queries:**
- "entity component system library"
- "ecs benchmark github"
- "rust ecs framework"
- "C# ecs game"
- "javascript ecs library"
- "data oriented design game"

---

#### 8. `roguelike-frameworks` — 8 repos → target 18+
**Missing:**
- NetHack (NetHack/NetHack, 3.5k) — classic roguelike
- Angband (angband/angband, 1.5k)
- Brogue CE (tmewett/BrogueCE, 1.3k)
- bracket-lib (amethyst/bracket-lib, 1.7k) — Rust RLTK
- SadConsole (Thraka/SadConsole, 1.4k) — .NET ASCII engine
- Cataclysm DDA/BN (~10k combined)
- Dungeon Template Library (AsPJT/DungeonTemplateLibrary, 1.4k)
- BearLibTerminal
- doryen-rs — Rust libtcod alternative

**Search queries:**
- "roguelike game open source"
- "ascii game engine"
- "roguelike development library"
- "dungeon generation library"
- "terminal game framework"

---

#### 9. `web-game-engines` — 8 repos → target 22+
**Missing:**
- Three.js (mrdoob/three.js, 111k) — web 3D
- melonJS (melonjs/melonJS, 6.7k)
- Excalibur (excaliburjs/Excalibur, 2k) — TypeScript 2D
- Kaplay (formerly Kaboom successor)
- ct.js (ct-js/ct-js) — visual game editor
- Kontra.js — micro game library
- Two.js (jonobr1/two.js, 8.2k) — 2D drawing API
- GDevelop web runtime
- Cocos Creator web
- A-Frame (aframevr/aframe) — WebXR

**Search queries:**
- "javascript game engine 2026"
- "typescript game framework"
- "webgpu game engine"
- "html5 game framework lightweight"
- "webxr game framework"

---

### Tier 2: Moderate Gaps (9-12 repos, research identified 50%+ more)

#### 10. `physics-engines` — 9 repos → target 18+
**Missing known repos:**
- Jolt Physics (jrouwe/JoltPhysics, 9.9k)
- matter.js (liabru/matter-js, 17.5k) — web 2D physics
- planck.js (shakiba/planck.js, 4.9k) — Box2D in JS
- cannon-es — 3D web physics
- dyn4j — Java 2D physics
- Oimo.js — lightweight 3D web physics
- ammo.js — Bullet compiled to JS

#### 11. `fluid-cloth-simulation` — 9 repos → target 16+
**Missing:**
- Taichi (taichi-dev/taichi, 26k) — GPU physics programming
- LiquidFun (google/liquidfun, 6.4k) — 2D fluid
- libigl (libigl/libigl, 4.7k) — geometry processing
- Flex (NVIDIA archived)
- Ten Minute Physics demos
- Various Unity/Godot cloth implementations

#### 12. `voxel-engines` — 9 repos → target 16+
**Missing:**
- Cuberite — C++ Minecraft server
- Craft (fogleman/Craft) — simple Minecraft clone
- Vintage Story modding ecosystem
- OpenVDB for games
- Various Rust voxel engines

#### 13. `game-networking` — 10 repos → target 20+
**Missing:**
- GameNetworkingSockets (ValveSoftware/GameNetworkingSockets, 9.3k)
- LiteNetLib (RevenantX/LiteNetLib, 3.4k)
- yojimbo (mas-bandwidth/yojimbo, 2.7k)
- Riptide Networking
- netcode.io protocol implementation
- WebRTC game networking libs
- Photon alternatives

#### 14. `emulators-retro` — 12 repos → target 35+
**Missing (huge gap — research identified 30+ emulators):**
- RetroArch/libretro (10k+)
- Dolphin (dolphin-emu/dolphin, 13k) — GameCube/Wii
- PCSX2 (PCSX2/pcsx2, 12k) — PS2
- RPCS3 (RPCS3/rpcs3, 15k) — PS3
- PPSSPP (hrydgard/ppsspp, 11k) — PSP
- mGBA (mgba-emu/mgba) — Game Boy Advance
- melonDS — Nintendo DS
- DeSmuME — Nintendo DS
- Citra/Lime3DS — 3DS
- Ryujinx — Nintendo Switch
- MAME (mamedev/mame) — arcade
- WASM-4 (aduros/wasm4) — fantasy console
- Mednafen, bsnes, Higan, ares
- Chip-8 implementations (dozens)

#### 15. `game-devops-analytics` — 13 repos → target 22+
**Missing:**
- PostHog (PostHog/posthog, 25k) — product analytics
- GrowthBook (growthbook/growthbook, 7k) — A/B testing
- Sentry game integrations (sentry-native, sentry-unreal, sentry-unity)
- Breakpad (google/breakpad, 1.5k) — crash reporting
- GameCI ecosystem (unity-builder, unity-test-runner, docker)
- FASTBuild (fastbuild/fastbuild, 1.2k) — distributed builds
- Steamworks.NET (rlabrecque/Steamworks.NET, 3.4k)

---

## Gap-Fill Execution Plan

### Wave 1: 8 agents, 15 tasks

| Task | Subdomain | Target Additional Repos |
|------|-----------|------------------------|
| 1 | emulators-retro-gap | +23 (biggest single gap) |
| 2 | web-game-engines-gap | +14 |
| 3 | ecs-frameworks-gap | +14 |
| 4 | game-scripting-gap | +12 |
| 5 | asset-tools-gap | +13 |
| 6 | game-audio-gap | +12 |
| 7 | roguelike-frameworks-gap | +10 |
| 8 | visual-novel-engines-gap | +13 |
| 9 | modding-frameworks-gap | +11 |
| 10 | game-server-orchestration-gap | +12 |
| 11 | physics-engines-gap | +9 |
| 12 | game-networking-gap | +10 |
| 13 | fluid-cloth-simulation-gap | +7 |
| 14 | voxel-engines-gap | +7 |
| 15 | game-devops-analytics-gap | +9 |

**Estimated yield:** +176 repos → **~512 total**

### Concat + Pipeline

After gap-fill discovery files land:
1. Concat gap-fill files into existing `raw-discovery.json`
2. Re-run dedup (cross-reference against existing 336)
3. Score, enrich, finalize → updated `catalog.json`

### Budget Estimate

- 8 Sonnet agents x ~3 min/task x 2 tasks each = ~50 min wall time
- 12 Haiku enrichment agents for new entries = ~2 min
- Pipeline (dedup + score + finalize) = ~30 sec
- **Total: ~55 min, ~$8-12 compute**
