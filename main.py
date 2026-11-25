"""
Manav Rachna Smart Campus Route Optimizer - College DAA Project Launcher.
Provides web server initialization and command-line benchmarking.
"""

import sys
import os
import argparse
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="Manav Rachna Smart Campus Route Optimizer (DAA Project)")
    parser.add_argument("--cli", action="store_true", help="Run benchmark suite directly in terminal")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address for web server")
    parser.add_argument("--port", type=int, default=8000, help="Port for web server")
    parser.add_argument("--reload", action="store_true", default=True, help="Auto-reload on code change")
    
    args = parser.parse_args()

    if args.cli:
        from benchmarks.benchmark_suite import BenchmarkSuite
        from algorithms.graph import CampusGraph

        json_path = os.path.join(os.path.dirname(__file__), "data", "campus_graph.json")
        graph = CampusGraph.from_json(json_path)
        suite = BenchmarkSuite(graph)

        print("\n=================================================================")
        print("  MANAV RACHNA SMART CAMPUS ROUTE OPTIMIZER - DAA BENCHMARK      ")
        print("=================================================================")
        print(f"Campus: Manav Rachna Educational Institutions (MREI)")
        print(f"Campus Graph: {graph.num_vertices()} Vertices, {graph.num_edges()} Edges")
        
        # Run default route
        res = suite.run_single_route_benchmark("N01", "N04", "distance", trials=50)
        print(f"\nRoute: {res['source']} -> {res['target']} | Mode: {res['cost_mode']}")
        print("-" * 75)
        print(f"{'Algorithm':<26} | {'Avg Time (ms)':<14} | {'Dist (m)':<10} | {'Big-O Time':<20}")
        print("-" * 75)
        for entry in res["comparison"]:
            avg_t = entry["timing"]["avg_ms"]
            dist = entry["total_distance"]
            comp = entry["time_complexity"]
            print(f"{entry['name']:<26} | {avg_t:<14.4f} | {dist:<10.1f} | {comp:<20}")
        print("=" * 75)
        sys.exit(0)

    print("\n=================================================================")
    print("   MANAV RACHNA SMART CAMPUS ROUTE OPTIMIZER - DAA EVALUATOR     ")
    print("=================================================================")
    print(f" Campus: Manav Rachna Educational Institutions (MRIIRS / MRU)")
    print(f" Starting web server on http://{args.host}:{args.port}")
    print(" Press Ctrl+C to terminate.")
    print("=================================================================\n")

    uvicorn.run("app:app", host=args.host, port=args.port, reload=args.reload)

if __name__ == "__main__":
    main()
