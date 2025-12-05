#!/usr/bin/env bash

# Consolidated prerequisite checking script
#
# This script provides unified prerequisite checking for Spec-Driven Development workflow.
# It replaces the functionality previously spread across multiple scripts.
#
# Usage: ./check-prerequisites.sh [OPTIONS]
#
# OPTIONS:
#   --json              Output in JSON format
#   --require-tasks     Require tasks.md to exist (for implementation phase)
#   --include-tasks     Include tasks.md in AVAILABLE_DOCS list
#   --paths-only        Only output path variables (no validation)
#   --help, -h          Show help message
#
# OUTPUTS:
#   JSON mode: {"FEATURE_DIR":"...", "AVAILABLE_DOCS":["..."]}
#   Text mode: FEATURE_DIR:... \n AVAILABLE_DOCS: \n ✓/✗ file.md
#   Paths only: REPO_ROOT: ... \n BRANCH: ... \n FEATURE_DIR: ... etc.

set -e



# EMBEDDED common.sh content START

#!/usr/bin/env bash

# Common functions and variables for all scripts



# Get repository root, with fallback for non-git repositories

get_repo_root() {

    if git rev-parse --show-toplevel >/dev/null 2>&1; then

        git rev-parse --show-toplevel

    else

        # Fall back to script location for non-git repos

        local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

        (cd "$script_dir/../../.." && pwd)

    fi

}



# Get current branch, with fallback for non-git repositories

get_current_branch() {

    # First check if SPECIFY_FEATURE environment variable is set

    if [[ -n "${SPECIFY_FEATURE:-}" ]]; then

        echo "$SPECIFY_FEATURE"

        return

    fi



    # Then check git if available

    if git rev-parse --abbrev-ref HEAD >/dev/null 2>&1; then

        git rev-parse --abbrev-ref HEAD

        return

    fi



    # For non-git repos, try to find the latest feature directory

    local repo_root=$(get_repo_root)

    local specs_dir="$repo_root/specs"



    if [[ -d "$specs_dir" ]]; then

        local latest_feature=""

        local highest=0



        for dir in "$specs_dir"/*; do

            if [[ -d "$dir" ]]; then

                local dirname=$(basename "$dir")

                if [[ "$dirname" =~ ^([0-9]{3})- ]]; then

                    local number=${BASH_REMATCH[1]}

                    number=$((10#$number))

                    if [[ "$number" -gt "$highest" ]]; then

                        highest=$number

                        latest_feature=$dirname

                    fi

                fi

            fi

        done



        if [[ -n "$latest_feature" ]]; then

            echo "$latest_feature"

            return

        fi

    fi



    echo "main"  # Final fallback

}



# Check if we have git available

has_git() {

    git rev-parse --show-toplevel >/dev/null 2>&1

}



check_feature_branch() {

    local branch="
"

    local has_git_repo="$2"



    # For non-git repos, we can't enforce branch naming but still provide output

    if [[ "$has_git_repo" != "true" ]]; then

        echo "[specify] Warning: Git repository not detected; skipped branch validation" >&2

        return 0

    fi



    if [[ ! "$branch" =~ ^[0-9]{3}- ]]; then

        echo "ERROR: Not on a feature branch. Current branch: $branch" >&2

        echo "Feature branches should be named like: 001-feature-name" >&2

        return 1

    fi



    return 0

}



get_feature_dir() { echo "
/specs/$2"; }



# Find feature directory by numeric prefix instead of exact branch match

# This allows multiple branches to work on the same spec (e.g., 004-fix-bug, 004-add-feature)

find_feature_dir_by_prefix() {

    local repo_root="
"

    local branch_name="$2"

    local specs_dir="$repo_root/specs"



    # Extract numeric prefix from branch (e.g., "004" from "004-whatever")

    if [[ ! "$branch_name" =~ ^([0-9]{3})- ]]; then

        # If branch doesn't have numeric prefix, fall back to exact match

        echo "$specs_dir/$branch_name"

        return

    fi



    local prefix="${BASH_REMATCH[1]}"



    # Search for directories in specs/ that start with this prefix

    local matches=()

    if [[ -d "$specs_dir" ]]; then

        for dir in "$specs_dir"/"$prefix"-*; do

            if [[ -d "$dir" ]]; then

                matches+=("$(basename "$dir")")

            fi

        done

    fi



    # Handle results

    if [[ ${#matches[@]} -eq 0 ]]; then

        # No match found - return the branch name path (will fail later with clear error)

        echo "$specs_dir/$branch_name"

    elif [[ ${#matches[@]} -eq 1 ]]; then

        # Exactly one match - perfect!

        echo "$specs_dir/${matches[0]}"

    else

        # Multiple matches - this shouldn't happen with proper naming convention

        echo "ERROR: Multiple spec directories found with prefix '$prefix': ${matches[*]}" >&2

        echo "Please ensure only one spec directory exists per numeric prefix." >&2

        echo "$specs_dir/$branch_name"  # Return something to avoid breaking the script

    fi

}



get_feature_paths() {

    local repo_root=$(get_repo_root)

    local current_branch=$(get_current_branch)

    local has_git_repo="false"



    if has_git; then

        has_git_repo="true"

    fi



    # Use prefix-based lookup to support multiple branches per spec

    local feature_dir=$(find_feature_dir_by_prefix "$repo_root" "$current_branch")



    cat <<EOF

REPO_ROOT='$repo_root'

CURRENT_BRANCH='$current_branch'

HAS_GIT='$has_git_repo'

FEATURE_DIR='$feature_dir'

FEATURE_SPEC='$feature_dir/spec.md'

IMPL_PLAN='$feature_dir/plan.md'

TASKS='$feature_dir/tasks.md'

RESEARCH='$feature_dir/research.md'

DATA_MODEL='$feature_dir/data-model.md'

QUICKSTART='$feature_dir/quickstart.md'

CONTRACTS_DIR='$feature_dir/contracts'

EOF

}



check_file() { [[ -f "
" ]] && echo "  ✓ $2" || echo "  ✗ $2"; }

check_dir() { [[ -d "
" && -n $(ls -A "
" 2>/dev/null) ]] && echo "  ✓ $2" || echo "  ✗ $2"; }

# EMBEDDED common.sh content END





# Parse command line arguments

JSON_MODE=false

REQUIRE_TASKS=false

INCLUDE_TASKS=false

PATHS_ONLY=false



for arg in "$@"; do

    case "$arg" in

        --json)

            JSON_MODE=true

            ;;

        --require-tasks)

            REQUIRE_TASKS=true

            ;;

        --include-tasks)

            INCLUDE_TASKS=true

            ;;

        --paths-only)

            PATHS_ONLY=true

            ;;

        --help|-h)

            cat << 'EOF'

Usage: check-prerequisites.sh [OPTIONS]

... (rest of the help message) ...

EOF

            exit 0

            ;;

        *)

            echo "ERROR: Unknown option '$arg'. Use --help for usage information." >&2

            exit 1

            ;;

    esac

done



# Get feature paths and validate branch

eval "$(get_feature_paths)"

check_feature_branch "$CURRENT_BRANCH" "$HAS_GIT" || exit 1



# If paths-only mode, output paths and exit (support JSON + paths-only combined)
if $PATHS_ONLY; then
    if $JSON_MODE; then
        # Minimal JSON paths payload (no validation performed)
        printf '{"REPO_ROOT":"%s","BRANCH":"%s","FEATURE_DIR":"%s","FEATURE_SPEC":"%s","IMPL_PLAN":"%s","TASKS":"%s"}\n' \
            "$REPO_ROOT" "$CURRENT_BRANCH" "$FEATURE_DIR" "$FEATURE_SPEC" "$IMPL_PLAN" "$TASKS"
    else
        echo "REPO_ROOT: $REPO_ROOT"
        echo "BRANCH: $CURRENT_BRANCH"
        echo "FEATURE_DIR: $FEATURE_DIR"
        echo "FEATURE_SPEC: $FEATURE_SPEC"
        echo "IMPL_PLAN: $IMPL_PLAN"
        echo "TASKS: $TASKS"
    fi
    exit 0
fi

# Validate required directories and files
if [[ ! -d "$FEATURE_DIR" ]]; then
    echo "ERROR: Feature directory not found: $FEATURE_DIR" >&2
    echo "Run /sp.specify first to create the feature structure." >&2
    exit 1
fi

if [[ ! -f "$IMPL_PLAN" ]]; then
    echo "ERROR: plan.md not found in $FEATURE_DIR" >&2
    echo "Run /sp.plan first to create the implementation plan." >&2
    exit 1
fi

# Check for tasks.md if required
if $REQUIRE_TASKS && [[ ! -f "$TASKS" ]]; then
    echo "ERROR: tasks.md not found in $FEATURE_DIR" >&2
    echo "Run /sp.tasks first to create the task list." >&2
    exit 1
fi

# Build list of available documents
docs=()

# Always check these optional docs
[[ -f "$RESEARCH" ]] && docs+=("research.md")
[[ -f "$DATA_MODEL" ]] && docs+=("data-model.md")

# Check contracts directory (only if it exists and has files)
if [[ -d "$CONTRACTS_DIR" ]] && [[ -n "$(ls -A "$CONTRACTS_DIR" 2>/dev/null)" ]]; then
    docs+=("contracts/")
fi

[[ -f "$QUICKSTART" ]] && docs+=("quickstart.md")

# Include tasks.md if requested and it exists
if $INCLUDE_TASKS && [[ -f "$TASKS" ]]; then
    docs+=("tasks.md")
fi

# Output results
if $JSON_MODE; then
    # Build JSON array of documents
    if [[ ${#docs[@]} -eq 0 ]]; then
        json_docs="[]"
    else
        json_docs=$(printf '"%s",' "${docs[@]}")
        json_docs="[${json_docs%,}]"
    fi
    
    printf '{"FEATURE_DIR":"%s","AVAILABLE_DOCS":%s}\n' "$FEATURE_DIR" "$json_docs"
else
    # Text output
    echo "FEATURE_DIR:$FEATURE_DIR"
    echo "AVAILABLE_DOCS:"
    
    # Show status of each potential document
    check_file "$RESEARCH" "research.md"
    check_file "$DATA_MODEL" "data-model.md"
    check_dir "$CONTRACTS_DIR" "contracts/"
    check_file "$QUICKSTART" "quickstart.md"
    
    if $INCLUDE_TASKS; then
        check_file "$TASKS" "tasks.md"
    fi
fi
