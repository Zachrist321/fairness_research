"""Quick Colab setup test — run this BEFORE the full generation script."""

from run_generation_supplement import preflight_check, MODELS, build_run_list

if __name__ == "__main__":
    preflight_check()
    runs, completed, v1_n, supp_n = build_run_list()
    print(f"Models configured: {MODELS}")
    print(f"V1 stories (skip): {v1_n}")
    print(f"Supplement checkpoint stories (skip): {supp_n}")
    print(f"Total already done: {len(completed)}")
    print(f"Still to generate: {len(runs)}")
    print("\nSetup looks good. Run:  !python run_generation_supplement.py")
