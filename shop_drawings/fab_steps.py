"""
TitanForge — Fabrication Step Templates
========================================
Defines step-by-step fabrication instructions per component type.
Ships with sensible defaults; admins can override per-component or per-job.

Each step has:
  - step_num: Sequential step number
  - title: Short action title
  - instruction: Detailed instruction text
  - safety: Optional safety note
  - tool: Tool/equipment required
  - estimated_minutes: Expected time for step
  - checkpoint: Whether this step requires a quality checkpoint
"""

import os
import json
from typing import List, Dict, Optional

# ─────────────────────────────────────────────
# DEFAULT FABRICATION STEPS BY COMPONENT TYPE
# ─────────────────────────────────────────────

DEFAULT_STEPS = {
    "column": [
        {
            "step_num": 1,
            "title": "Pull Material",
            "instruction": "Pull two (2) 14\"x4\" CEE sections from C2 roll former output rack. "
                           "Verify gauge (10GA) and length match the shop drawing. "
                           "Check for damage, kinks, or coating defects.",
            "safety": "Wear cut-resistant gloves when handling raw steel.",
            "tool": "Tape measure, marker",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
        {
            "step_num": 2,
            "title": "Align & Clamp CEEs",
            "instruction": "Place both CEE sections back-to-back on the welding table. "
                           "Align ends flush using the stop block. Clamp at both ends "
                           "and at 4-foot intervals along the length. Verify square "
                           "using a framing square at both ends.",
            "safety": "",
            "tool": "Welding table, bar clamps, framing square",
            "estimated_minutes": 8,
            "checkpoint": False,
        },
        {
            "step_num": 3,
            "title": "Tack Weld",
            "instruction": "Apply tack welds per WPS-\"B\" at 12\" intervals along both "
                           "seams (top and bottom). Start from center, work outward to "
                           "prevent warping. Each tack should be 3/4\" long minimum.",
            "safety": "Full welding PPE required: auto-darkening helmet, welding gloves, leather apron.",
            "tool": "MIG welder, WPS-B settings",
            "estimated_minutes": 12,
            "checkpoint": False,
        },
        {
            "step_num": 4,
            "title": "Stitch Weld",
            "instruction": "Run stitch welds per WPS-\"B\": 1.5\" welds at 12\" on-center "
                           "along both seams. Maintain consistent travel speed. "
                           "Do NOT run continuous welds — stitch pattern prevents warping.",
            "safety": "Ensure adequate ventilation. Keep fire extinguisher within reach.",
            "tool": "MIG welder, WPS-B settings",
            "estimated_minutes": 20,
            "checkpoint": False,
        },
        {
            "step_num": 5,
            "title": "Weld End Plates",
            "instruction": "Fit and weld end plates per WPS-\"F\" at both ends of the column. "
                           "Ensure plates are square to the column axis. Full perimeter weld "
                           "required on both plates.",
            "safety": "",
            "tool": "MIG welder, WPS-F settings, framing square",
            "estimated_minutes": 15,
            "checkpoint": False,
        },
        {
            "step_num": 6,
            "title": "Attach Rebar (if applicable)",
            "instruction": "If rebar is specified on the shop drawing, weld rebar sections "
                           "to the column per WPS-\"D\". Check drawing for rebar locations, "
                           "lengths, and quantities.",
            "safety": "Rebar ends are sharp — handle with care.",
            "tool": "MIG welder, WPS-D settings",
            "estimated_minutes": 10,
            "checkpoint": False,
        },
        {
            "step_num": 7,
            "title": "Weld Purlin Clips",
            "instruction": "Weld purlin clips to column per WPS-\"C\" at positions shown on "
                           "the shop drawing. Verify clip spacing matches the purlin layout. "
                           "Clips must be oriented correctly (open side faces the correct direction).",
            "safety": "",
            "tool": "MIG welder, WPS-C settings, tape measure",
            "estimated_minutes": 15,
            "checkpoint": False,
        },
        {
            "step_num": 8,
            "title": "Clean Welds",
            "instruction": "Grind all weld spatter. Wire brush all weld areas. "
                           "Apply cold galvanizing compound (ZRC) to all weld zones. "
                           "Allow 15 minutes cure time.",
            "safety": "Wear safety glasses and dust mask when grinding.",
            "tool": "Angle grinder, wire wheel, ZRC spray",
            "estimated_minutes": 15,
            "checkpoint": False,
        },
        {
            "step_num": 9,
            "title": "Quality Inspection",
            "instruction": "Inspect all welds for: proper size, no porosity, no undercut, "
                           "no cracks. Verify overall length matches drawing +/- 1/8\". "
                           "Check squareness of end plates. Verify clip positions. "
                           "Mark PASS/FAIL on the QC tag.",
            "safety": "",
            "tool": "Fillet gauge, tape measure, framing square",
            "estimated_minutes": 10,
            "checkpoint": True,
        },
        {
            "step_num": 10,
            "title": "Tag & Stage",
            "instruction": "Attach the ship mark sticker in a visible location. "
                           "Move column to the staging area for the job. "
                           "Log completion on the work order.",
            "safety": "Use overhead crane or forklift for columns over 20 feet.",
            "tool": "Sticker, marker, overhead crane",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
    ],

    "rafter": [
        {
            "step_num": 1,
            "title": "Pull Material",
            "instruction": "Pull two (2) 14\"x4\" CEE sections from C2 output rack. "
                           "Verify gauge and length match shop drawing. "
                           "Also pull the peak cap and any required peak gussets.",
            "safety": "Wear cut-resistant gloves.",
            "tool": "Tape measure, marker",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
        {
            "step_num": 2,
            "title": "Mark Pitch Cut",
            "instruction": "Using the shop drawing, mark the pitch cut angle on one end "
                           "of each CEE. The pitch angle is shown on the rafter detail. "
                           "Double-check the angle before cutting.",
            "safety": "",
            "tool": "Protractor, speed square, marker",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
        {
            "step_num": 3,
            "title": "Cut Pitch Angle",
            "instruction": "Cut the pitch angle on the marked CEE ends using the chop saw. "
                           "Deburr all cut edges.",
            "safety": "Eye and ear protection required for cutting.",
            "tool": "Chop saw, deburring tool",
            "estimated_minutes": 8,
            "checkpoint": False,
        },
        {
            "step_num": 4,
            "title": "Align & Clamp CEEs",
            "instruction": "Place both CEE sections back-to-back on the rafter jig. "
                           "The pitch-cut ends meet at the peak. Align carefully and "
                           "clamp at peak, eave, and every 4 feet.",
            "safety": "",
            "tool": "Rafter jig, bar clamps, framing square",
            "estimated_minutes": 10,
            "checkpoint": False,
        },
        {
            "step_num": 5,
            "title": "Tack Weld",
            "instruction": "Tack weld per WPS-\"B\" at 12\" intervals along both seams. "
                           "Start from center, work outward.",
            "safety": "Full welding PPE required.",
            "tool": "MIG welder, WPS-B settings",
            "estimated_minutes": 10,
            "checkpoint": False,
        },
        {
            "step_num": 6,
            "title": "Stitch Weld",
            "instruction": "Run stitch welds per WPS-\"B\": 1.5\" welds at 12\" on-center. "
                           "Both seams, full length.",
            "safety": "Adequate ventilation required.",
            "tool": "MIG welder, WPS-B settings",
            "estimated_minutes": 20,
            "checkpoint": False,
        },
        {
            "step_num": 7,
            "title": "Weld Peak Cap & Eave Plates",
            "instruction": "Fit peak cap over the peak joint. Weld per WPS-\"F\". "
                           "Weld eave connection plates at the column end per WPS-\"F\".",
            "safety": "",
            "tool": "MIG welder, WPS-F settings",
            "estimated_minutes": 15,
            "checkpoint": False,
        },
        {
            "step_num": 8,
            "title": "Weld Purlin Clips",
            "instruction": "Weld purlin clips per WPS-\"C\" at positions shown on shop drawing. "
                           "Verify spacing from eave and between clips. Check clip orientation.",
            "safety": "",
            "tool": "MIG welder, WPS-C settings, tape measure",
            "estimated_minutes": 15,
            "checkpoint": False,
        },
        {
            "step_num": 9,
            "title": "Clean Welds & Galvanize",
            "instruction": "Grind spatter, wire brush all weld areas. Apply ZRC cold galv "
                           "to all weld zones. Allow cure time.",
            "safety": "Dust mask and safety glasses for grinding.",
            "tool": "Angle grinder, wire wheel, ZRC spray",
            "estimated_minutes": 15,
            "checkpoint": False,
        },
        {
            "step_num": 10,
            "title": "Quality Inspection",
            "instruction": "Inspect all welds per QC checklist. Verify rafter length, "
                           "pitch angle, clip positions. Check peak cap alignment. "
                           "Mark PASS/FAIL on QC tag.",
            "safety": "",
            "tool": "Fillet gauge, protractor, tape measure",
            "estimated_minutes": 10,
            "checkpoint": True,
        },
        {
            "step_num": 11,
            "title": "Tag & Stage",
            "instruction": "Attach ship mark sticker. Move rafter to job staging area. "
                           "Log completion.",
            "safety": "Use overhead crane for rafters.",
            "tool": "Sticker, overhead crane",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
    ],

    "purlin": [
        {
            "step_num": 1,
            "title": "Check Roll Former Setup",
            "instruction": "Verify the roll former is set to the correct purlin profile "
                           "(C-purlin on C1 or Z-purlin on Z1). Check web depth, flange width, "
                           "and lip dimension match the shop drawing spec.",
            "safety": "Lock-out/tag-out if adjusting die sets.",
            "tool": "Calipers, tape measure",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
        {
            "step_num": 2,
            "title": "Load Coil",
            "instruction": "If coil needs changing, load the correct gauge and width coil "
                           "onto the decoiler. Thread through the roll former. "
                           "Verify coil material (gauge, grade) matches the BOM.",
            "safety": "Never reach into the decoiler while running. Keep hands clear of pinch points.",
            "tool": "Forklift (for coil), coil cradle",
            "estimated_minutes": 10,
            "checkpoint": False,
        },
        {
            "step_num": 3,
            "title": "Program Lengths",
            "instruction": "Enter the cut lengths from the shop drawing into the roll former "
                           "controller. Set the quantity for each length. Verify punch pattern "
                           "is correct for the purlin type.",
            "safety": "",
            "tool": "Roll former controller",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
        {
            "step_num": 4,
            "title": "Run Purlins",
            "instruction": "Run the programmed batch. Catch each purlin as it exits and "
                           "stack neatly on the output rack. Verify the first piece "
                           "against the drawing before running the full batch.",
            "safety": "Keep hands clear of the shear. Wear hearing protection.",
            "tool": "Roll former, output rack",
            "estimated_minutes": 20,
            "checkpoint": False,
        },
        {
            "step_num": 5,
            "title": "First Article Check",
            "instruction": "Measure the first purlin: overall length, web depth, flange width, "
                           "lip dimension, hole locations. All must be within +/- 1/16\" of drawing. "
                           "If out of spec, adjust and re-run.",
            "safety": "",
            "tool": "Tape measure, calipers",
            "estimated_minutes": 5,
            "checkpoint": True,
        },
        {
            "step_num": 6,
            "title": "Bundle & Tag",
            "instruction": "Bundle purlins by group (per shop drawing). Band with steel straps "
                           "at 4-foot intervals. Attach ship mark sticker to the bundle tag. "
                           "Move to staging area.",
            "safety": "Use proper lifting technique — purlins can be long and unwieldy.",
            "tool": "Banding tool, stickers",
            "estimated_minutes": 10,
            "checkpoint": False,
        },
    ],

    "sag_rod": [
        {
            "step_num": 1,
            "title": "Check Angle Machine Setup",
            "instruction": "Verify the angle machine is set for 2\"x2\" angle. "
                           "Check the stop for the correct cut length per shop drawing.",
            "safety": "Lock-out/tag-out if adjusting.",
            "tool": "Tape measure",
            "estimated_minutes": 3,
            "checkpoint": False,
        },
        {
            "step_num": 2,
            "title": "Cut Sag Rods",
            "instruction": "Cut the quantity of sag rods specified on the shop drawing. "
                           "Deburr all cut ends. Stack neatly.",
            "safety": "Eye protection required.",
            "tool": "Angle machine, deburring tool",
            "estimated_minutes": 10,
            "checkpoint": False,
        },
        {
            "step_num": 3,
            "title": "Bundle & Tag",
            "instruction": "Bundle sag rods and attach the ship mark sticker. "
                           "Move to staging area.",
            "safety": "",
            "tool": "Wire ties, sticker",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
    ],

    "clip": [
        {
            "step_num": 1,
            "title": "Check Plate Former Setup",
            "instruction": "Verify P1 plate former is set for the correct clip type "
                           "(P1 standard clip or P2 eave cap clip). Check dimensions "
                           "against the shop drawing.",
            "safety": "Lock-out/tag-out if adjusting.",
            "tool": "Calipers",
            "estimated_minutes": 3,
            "checkpoint": False,
        },
        {
            "step_num": 2,
            "title": "Run Clips",
            "instruction": "Run the quantity specified on the shop drawing. "
                           "Verify first piece dimensions before running the full batch.",
            "safety": "Keep hands clear of the press.",
            "tool": "P1 plate former",
            "estimated_minutes": 10,
            "checkpoint": False,
        },
        {
            "step_num": 3,
            "title": "Count & Bag",
            "instruction": "Count clips to verify quantity. Bag with ship mark label. "
                           "Move to staging area.",
            "safety": "",
            "tool": "Bags, sticker",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
    ],

    "panel": [
        {
            "step_num": 1,
            "title": "Check Panel Roll Former",
            "instruction": "Verify the Spartan Rib roll former is set up correctly. "
                           "Check panel width (covers 36\" net) and rib profile.",
            "safety": "Lock-out/tag-out if adjusting.",
            "tool": "Tape measure",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
        {
            "step_num": 2,
            "title": "Load Coil",
            "instruction": "Load the correct coil (48\" wide, 29GA, G50). "
                           "Verify color/finish matches the job spec. "
                           "Thread through the roll former.",
            "safety": "Never reach into decoiler while running.",
            "tool": "Forklift, coil cradle",
            "estimated_minutes": 10,
            "checkpoint": False,
        },
        {
            "step_num": 3,
            "title": "Program Panel Lengths",
            "instruction": "Enter panel lengths from the shop drawing into the controller. "
                           "Set quantities for each length.",
            "safety": "",
            "tool": "Roll former controller",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
        {
            "step_num": 4,
            "title": "Run Panels",
            "instruction": "Run the programmed batch. Handle panels carefully to avoid "
                           "scratching the painted surface. Stack with foam spacers.",
            "safety": "Wear gloves — panel edges are sharp.",
            "tool": "Roll former, foam spacers",
            "estimated_minutes": 20,
            "checkpoint": False,
        },
        {
            "step_num": 5,
            "title": "First Article Check",
            "instruction": "Measure first panel length and width. Check rib alignment. "
                           "Verify no scratches or dents.",
            "safety": "",
            "tool": "Tape measure",
            "estimated_minutes": 5,
            "checkpoint": True,
        },
        {
            "step_num": 6,
            "title": "Bundle & Tag",
            "instruction": "Stack panels on a pallet with edge protectors. "
                           "Band the bundle. Attach ship mark sticker. "
                           "Cover with weather wrap if storing outside.",
            "safety": "Use forklift for moving panel bundles.",
            "tool": "Banding tool, edge protectors, sticker",
            "estimated_minutes": 10,
            "checkpoint": False,
        },
    ],

    "trim": [
        {
            "step_num": 1,
            "title": "Set Up Brake",
            "instruction": "Set the trim brake to the correct profile per the shop drawing. "
                           "Install the proper tooling for the trim type (ridge cap, corner, "
                           "rake, eave, etc.).",
            "safety": "Lock-out/tag-out when changing tooling.",
            "tool": "Trim brake",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
        {
            "step_num": 2,
            "title": "Cut & Form Trim",
            "instruction": "Cut flat stock to length, then form through the brake. "
                           "Verify profile matches the shop drawing.",
            "safety": "Gloves required — trim edges are sharp.",
            "tool": "Shear, trim brake",
            "estimated_minutes": 15,
            "checkpoint": False,
        },
        {
            "step_num": 3,
            "title": "Bundle & Tag",
            "instruction": "Bundle trim pieces by type. Attach ship mark sticker. "
                           "Move to staging area.",
            "safety": "",
            "tool": "Sticker, banding tool",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
    ],

    "strap": [
        {
            "step_num": 1,
            "title": "Cut Flat Stock",
            "instruction": "Cut 1.5\" x 10GA flat strap to length per shop drawing. "
                           "Verify dimensions against drawing before proceeding.",
            "safety": "Wear cut-resistant gloves when handling raw steel.",
            "tool": "Shear or chop saw, tape measure",
            "estimated_minutes": 3,
            "checkpoint": False,
        },
        {
            "step_num": 2,
            "title": "Drill Holes",
            "instruction": "Drill bolt holes per the hole pattern on the shop drawing. "
                           "Use drill press for consistency. Deburr all holes.",
            "safety": "Eye protection required. Clamp workpiece securely.",
            "tool": "Drill press, step drill, deburring tool",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
        {
            "step_num": 3,
            "title": "Form Bends",
            "instruction": "If strap requires bends, form on the brake per drawing detail. "
                           "Verify bend radius and angle match spec.",
            "safety": "Keep fingers clear of brake dies.",
            "tool": "Press brake or bench vise",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
        {
            "step_num": 4,
            "title": "QC & Tag",
            "instruction": "Verify all dimensions against shop drawing. "
                           "Apply ship mark sticker. Bundle like straps together.",
            "safety": "",
            "tool": "Tape measure, sticker",
            "estimated_minutes": 3,
            "checkpoint": True,
        },
    ],

    "endcap": [
        {
            "step_num": 1,
            "title": "Cut U-Channel",
            "instruction": "Cut U-channel to length per shop drawing. "
                           "Verify dimensions and squareness of cut.",
            "safety": "Wear cut-resistant gloves.",
            "tool": "Chop saw, tape measure, square",
            "estimated_minutes": 3,
            "checkpoint": False,
        },
        {
            "step_num": 2,
            "title": "Drill Mounting Holes",
            "instruction": "Drill bolt holes per the hole pattern on the shop drawing. "
                           "Use drill press for consistency. Deburr all holes.",
            "safety": "Eye protection required. Clamp workpiece securely.",
            "tool": "Drill press, step drill, deburring tool",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
        {
            "step_num": 3,
            "title": "QC & Tag",
            "instruction": "Verify all dimensions against shop drawing. "
                           "Apply ship mark sticker. Bundle like endcaps together.",
            "safety": "",
            "tool": "Tape measure, sticker",
            "estimated_minutes": 3,
            "checkpoint": True,
        },
    ],

    "p2plate": [
        {
            "step_num": 1,
            "title": "Cut Plate",
            "instruction": "Cut 9\"x24\" eave plate from flat stock per shop drawing. "
                           "Verify dimensions before proceeding.",
            "safety": "Wear cut-resistant gloves.",
            "tool": "Shear or plasma cutter, tape measure",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
        {
            "step_num": 2,
            "title": "Drill Hole Pattern",
            "instruction": "Drill bolt holes per the pattern on the shop drawing. "
                           "Use drill press for consistency. Deburr all holes.",
            "safety": "Eye protection required. Clamp workpiece securely.",
            "tool": "Drill press, step drill, deburring tool",
            "estimated_minutes": 8,
            "checkpoint": False,
        },
        {
            "step_num": 3,
            "title": "Form L-Bend",
            "instruction": "Form the L-bend per the shop drawing side view. "
                           "Verify bend angle and dimension match spec.",
            "safety": "Keep fingers clear of brake dies.",
            "tool": "Press brake",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
        {
            "step_num": 4,
            "title": "QC & Tag",
            "instruction": "Verify all dimensions and hole pattern against shop drawing. "
                           "Apply ship mark sticker.",
            "safety": "",
            "tool": "Tape measure, sticker",
            "estimated_minutes": 3,
            "checkpoint": True,
        },
    ],

    "splice": [
        {
            "step_num": 1,
            "title": "Cut Plate",
            "instruction": "Cut splice plate to size per shop drawing. "
                           "Verify dimensions and squareness.",
            "safety": "Wear cut-resistant gloves.",
            "tool": "Shear or plasma cutter, tape measure, square",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
        {
            "step_num": 2,
            "title": "Drill Bolt Pattern",
            "instruction": "Drill bolt holes per the pattern on the shop drawing. "
                           "Use drill press with template jig for consistency. "
                           "Deburr all holes.",
            "safety": "Eye protection required. Clamp workpiece securely.",
            "tool": "Drill press, template jig, step drill, deburring tool",
            "estimated_minutes": 10,
            "checkpoint": False,
        },
        {
            "step_num": 3,
            "title": "Verify Bolt Pattern",
            "instruction": "Check all hole locations against shop drawing using go/no-go gauge. "
                           "Verify bolt spacing, edge distance, and alignment. "
                           "This is critical — misaligned splice plates cause field failures.",
            "safety": "",
            "tool": "Go/no-go gauge, calipers, shop drawing",
            "estimated_minutes": 5,
            "checkpoint": True,
        },
        {
            "step_num": 4,
            "title": "QC & Tag",
            "instruction": "Final dimensional check. Mark splice plate pairs (L/R). "
                           "Apply ship mark sticker with torque spec reference.",
            "safety": "",
            "tool": "Tape measure, sticker, marker",
            "estimated_minutes": 3,
            "checkpoint": True,
        },
    ],
}

# Component type aliases — map item component_types to step template keys
COMPONENT_TYPE_MAP = {
    "column": "column",
    "rafter": "rafter",
    "purlin": "purlin",
    "z_purlin": "purlin",
    "c_purlin": "purlin",
    "purlin_group": "purlin",
    "sag_rod": "sag_rod",
    "sag_rods": "sag_rod",
    "clip": "clip",
    "p1_clip": "clip",
    "p2_clip": "clip",
    "hurricane_strap": "strap",
    "strap": "strap",
    "endcap": "endcap",
    "end_cap": "endcap",
    "u_channel": "endcap",
    "p1clip": "clip",
    "p2plate": "p2plate",
    "p2_plate": "p2plate",
    "eave_plate": "p2plate",
    "splice": "splice",
    "splice_plate": "splice",
    "panel": "panel",
    "roofing_panel": "panel",
    "wall_panel": "panel",
    "trim": "trim",
    "ridge_cap": "trim",
    "eave_trim": "trim",
    "rake_trim": "trim",
    "corner_trim": "trim",
}


# ─────────────────────────────────────────────
# STEP TEMPLATE MANAGEMENT
# ─────────────────────────────────────────────

def get_steps_for_item(item_dict: dict, base_dir: str = "",
                       job_code: str = "") -> List[dict]:
    """Get fabrication steps for a work order item.

    Priority:
      1. Job-specific override (data/shop_drawings/{job_code}/fab_steps/{component_type}.json)
      2. Global override (data/shop_drawings/_fab_steps/{component_type}.json)
      3. Default steps from DEFAULT_STEPS

    Args:
        item_dict: WorkOrderItem.to_dict() result
        base_dir: Shop drawings data directory
        job_code: Job code for job-specific overrides

    Returns:
        List of step dicts with step_num, title, instruction, safety, tool, etc.
    """
    component_type = item_dict.get("component_type", "")
    template_key = COMPONENT_TYPE_MAP.get(component_type, component_type)

    # 1. Check job-specific override
    if base_dir and job_code:
        job_steps_file = os.path.join(
            base_dir, job_code, "fab_steps", f"{template_key}.json"
        )
        if os.path.isfile(job_steps_file):
            try:
                with open(job_steps_file) as f:
                    return json.load(f)
            except Exception:
                pass

    # 2. Check global override
    if base_dir:
        global_steps_file = os.path.join(
            base_dir, "_fab_steps", f"{template_key}.json"
        )
        if os.path.isfile(global_steps_file):
            try:
                with open(global_steps_file) as f:
                    return json.load(f)
            except Exception:
                pass

    # 3. Fall back to defaults
    return DEFAULT_STEPS.get(template_key, _generic_steps(component_type))


def save_step_override(base_dir: str, template_key: str,
                       steps: List[dict], job_code: str = "") -> str:
    """Save custom step template (global or job-specific).

    Args:
        base_dir: Shop drawings data directory
        template_key: Component type key (e.g., "column", "rafter")
        steps: List of step dicts
        job_code: If provided, saves as job-specific override

    Returns:
        Path to the saved file
    """
    if job_code:
        dir_path = os.path.join(base_dir, job_code, "fab_steps")
    else:
        dir_path = os.path.join(base_dir, "_fab_steps")

    os.makedirs(dir_path, exist_ok=True)
    filepath = os.path.join(dir_path, f"{template_key}.json")

    with open(filepath, "w") as f:
        json.dump(steps, f, indent=2)

    return filepath


def list_available_templates() -> Dict[str, int]:
    """List all default step templates and their step counts."""
    return {k: len(v) for k, v in DEFAULT_STEPS.items()}


def _generic_steps(component_type: str) -> List[dict]:
    """Generate generic steps for an unknown component type."""
    return [
        {
            "step_num": 1,
            "title": "Review Drawing",
            "instruction": f"Review the shop drawing for this {component_type} component. "
                           "Note dimensions, material spec, and any special requirements.",
            "safety": "",
            "tool": "Shop drawing",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
        {
            "step_num": 2,
            "title": "Pull Material",
            "instruction": f"Pull the required material for this {component_type}. "
                           "Verify material type, gauge, and quantity against the BOM.",
            "safety": "Wear appropriate PPE for material handling.",
            "tool": "As required",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
        {
            "step_num": 3,
            "title": "Fabricate",
            "instruction": f"Fabricate the {component_type} per the shop drawing specifications. "
                           "Follow all applicable WPS codes.",
            "safety": "Follow all shop safety procedures.",
            "tool": "As specified on drawing",
            "estimated_minutes": 30,
            "checkpoint": False,
        },
        {
            "step_num": 4,
            "title": "Quality Check",
            "instruction": "Verify all dimensions and weld quality. "
                           "Compare finished piece against the shop drawing.",
            "safety": "",
            "tool": "Tape measure, fillet gauge",
            "estimated_minutes": 10,
            "checkpoint": True,
        },
        {
            "step_num": 5,
            "title": "Tag & Stage",
            "instruction": "Attach ship mark sticker. Move to staging area. "
                           "Log completion.",
            "safety": "",
            "tool": "Sticker",
            "estimated_minutes": 5,
            "checkpoint": False,
        },
    ]
