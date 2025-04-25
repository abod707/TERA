import time
import requests
from agents import Runner
from duckduckgo_search import DDGS
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from models import SearchResult
from research_agents.follow_up_agent import FollowUpDecisionResponse

console = Console()

class ResearchCoordinator:
    def __init__(self, query: str, query_agent, search_agent, follow_up_decision_agent, synthesis_agent, mode: str, search_provider: str, serper_api_key: str, brave_api_key: str):
        self.query = query
        self.search_results = []
        self.iteration = 1
        self.total_queries = 0  # Track total queries executed
        self.total_results = 0  # Track total results processed
        self.mode = mode  # '1' for normal, '2' for deep
        self.search_provider = search_provider  # 'duckduckgo', 'serper', or 'brave'
        self.query_agent = query_agent
        self.search_agent = search_agent
        self.follow_up_decision_agent = follow_up_decision_agent
        self.synthesis_agent = synthesis_agent
        self.serper_api_key = serper_api_key
        self.brave_api_key = brave_api_key

    async def research(self) -> str:
        query_response = await self.generate_queries()
        await self.perform_research_for_queries(queries=query_response.queries)

        # In normal mode, no follow-up iterations; in deep mode, allow more iterations
        max_iterations = 1 if self.mode == "1" else 4  # Deep mode can have up to 4 iterations
        if self.mode == "1":
            console.print("[cyan]Normal mode: No follow-up iterations allowed.[/cyan]")
        else:
            while self.iteration < max_iterations and self.follow_up_decision_agent:
                decision_response = await self.generate_followup()
                if not decision_response.should_follow_up:
                    console.print("[cyan]No more research needed. Synthesizing report...[/cyan]")
                    break
                self.iteration += 1
                console.print(f"[cyan]Conducting follow-up research (iteration {self.iteration})...[/cyan]")
                await self.perform_research_for_queries(queries=decision_response.queries)

        final_report = await self.synthesis_report()
        console.print(f"\n[bold green]✓ Research complete![/bold green] Processed {self.total_queries} queries across {self.iteration} iteration(s), with {len(self.search_results)} total results.\n")
        return final_report

    async def generate_queries(self):
        with console.status("[bold cyan]Analyzing query...[/bold cyan]") as status:
            result = await Runner.run(self.query_agent, input=self.query)
            console.print(Panel(f"[bold cyan]Query Analysis[/bold cyan]"))
            console.print(f"[yellow]Thoughts:[/yellow] {result.final_output.thoughts}")
            console.print("\n[yellow]Generated Search Queries:[/yellow]")
            # In normal mode, cap at 5 total queries; in deep mode, take up to 3 queries per iteration
            queries = result.final_output.queries
            if self.mode == "1":
                remaining_queries = max(0, 5 - self.total_queries)
                queries = queries[:remaining_queries]
            else:
                queries = queries[:3]  # Deep mode: up to 3 queries per iteration
            for i, query in enumerate(queries, 1):
                console.print(f"  {i}. {query}")
            return result.final_output

    def search(self, query: str):
        try:
            if self.search_provider == "duckduckgo":
                max_results = 2 if self.mode == "1" else 5
                results = DDGS().text(query, region='us-en', safesearch='on', timelimit='y', max_results=max_results)
                results = [{"title": r["title"], "href": r["href"]} for r in results]
                return results[:max_results]  # Strictly enforce the max_results limit
            elif self.search_provider == "serper":
                max_results = 2 if self.mode == "1" else 5
                headers = {"X-API-KEY": self.serper_api_key}
                response = requests.post(
                    "https://google.serper.dev/search",
                    json={"q": query, "num": max_results},
                    headers=headers
                )
                response.raise_for_status()
                results = response.json().get("organic", [])
                results = [{"title": r["title"], "href": r["link"]} for r in results]
                return results[:max_results]  # Strictly enforce the max_results limit
            elif self.search_provider == "brave":
                max_results = 2 if self.mode == "1" else 5
                headers = {"X-Subscription-Token": self.brave_api_key}
                params = {"q": query, "count": max_results, "country": "us"}
                response = requests.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                results = response.json().get("web", {}).get("results", [])
                results = [{"title": r["title"], "href": r["url"]} for r in results]
                return results[:max_results]  # Strictly enforce the max_results limit
            else:
                return []
        except Exception as ex:
            console.print(f"[bold red]Search error ({self.search_provider}):[/bold red] {str(ex)}")
            return []

    async def perform_research_for_queries(self, queries: list[str]) -> None:
        all_search_results = {}
        max_total_results = 6 if self.mode == "1" else float('inf')  # No cap in deep mode

        for query in queries:
            if self.mode == "1" and self.total_queries >= 5:
                console.print("[cyan]Normal mode query limit (5) reached. Skipping further queries...[/cyan]")
                break
            self.total_queries += 1
            search_results = self.search(query)
            all_search_results[query] = search_results
            console.print(f"[cyan]Using {self.search_provider} for query: {query}[/cyan]")

        for query, results in all_search_results.items():
            console.print(f"\n[bold cyan]Searching for (via {self.search_provider}):[/bold cyan] {query}")
            for result in results:
                if self.mode == "1" and self.total_results >= max_total_results:
                    console.print("[cyan]Normal mode result limit (6) reached. Skipping further results...[/cyan]")
                    break
                self.total_results += 1
                console.print(f"  [green]Result:[/green] {result['title']}")
                console.print(f"  [dim]URL:[/dim] {result['href']}")
                console.print(f"  [cyan]Analyzing content...[/cyan]")
                start_analysis_time = time.time()
                search_input = f"Title: {result['title']}\nURL: {result['href']}"
                agent_result = await Runner.run(self.search_agent, input=search_input)
                analysis_time = time.time() - start_analysis_time
                search_result = SearchResult(
                    title=result['title'],
                    url=result['href'],
                    summary=agent_result.final_output
                )
                self.search_results.append(search_result)
                summary_preview = agent_result.final_output[:100] + ("..." if len(agent_result.final_output) > 100 else "")
                console.print(f"  [green]Summary:[/green] {summary_preview}")
                console.print(f"  [dim]Analysis completed in {analysis_time:.2f}s[/dim]\n")
        console.print(f"\n[bold green]✓ Research round complete![/bold green] Found {len(self.search_results)} total results in this iteration with {len(queries)} queries.")

    async def synthesis_report(self) -> str:
        with console.status("[bold cyan]Synthesizing research findings...[/bold cyan]") as status:
            if self.mode == "1" or len(self.search_results) <= 15:
                # For normal mode or small result sets, synthesize all at once
                findings_text = f"Query: {self.query}\n\nSearch Results:\n"
                for i, result in enumerate(self.search_results, 1):
                    findings_text += f"\n{i}. Title: {result.title}\n   URL: {result.url}\n   Summary: {result.summary}\n"
                result = await Runner.run(self.synthesis_agent, input=findings_text)
                return result.final_output
            else:
                # For deep mode with large result sets, chunk the results
                chunk_size = 15
                partial_reports = []
                for i in range(0, len(self.search_results), chunk_size):
                    chunk = self.search_results[i:i + chunk_size]
                    findings_text = f"Query: {self.query}\n\nSearch Results:\n"
                    for j, result in enumerate(chunk, 1):
                        findings_text += f"\n{j}. Title: {result.title}\n   URL: {result.url}\n   Summary: {result.summary}\n"
                    result = await Runner.run(self.synthesis_agent, input=findings_text)
                    partial_reports.append(result.final_output)
                
                # Combine partial reports into a final report
                combined_report = f"# Comprehensive Report on {self.query}\n\n"
                for idx, partial_report in enumerate(partial_reports, 1):
                    combined_report += f"## Part {idx}\n\n{partial_report}\n\n"
                
                # Optional: Add a final synthesis step to summarize the combined report
                final_synthesis_input = f"Query: {self.query}\n\nPartial Reports:\n"
                for idx, partial_report in enumerate(partial_reports, 1):
                    final_synthesis_input += f"\nPart {idx}:\n{partial_report}\n"
                final_result = await Runner.run(
                    self.synthesis_agent,
                    input=final_synthesis_input + "\nSynthesize these partial reports into a cohesive final report, ensuring all sections are covered and the total length meets the deep mode requirements (1000+ words for 16+ results)."
                )
                return final_result.final_output

    async def generate_followup(self) -> FollowUpDecisionResponse:
        with console.status("[bold cyan]Evaluating if more research is needed...[/bold cyan]") as status:
            findings_text = f"Original Query: {self.query}\n\nCurrent Findings:\n"
            for i, result in enumerate(self.search_results, 1):
                findings_text += f"\n{i}. Title: {result.title}\n   URL: {result.url}\n   Summary: {result.summary}\n"
            result = await Runner.run(self.follow_up_decision_agent, input=findings_text)
            console.print(Panel(f"[bold cyan]Follow-up Decision[/bold cyan]"))
            console.print(f"[yellow]Decision:[/yellow] {'More research needed' if result.final_output.should_follow_up else 'Research complete'}")
            console.print(f"[yellow]Reasoning:[/yellow] {result.final_output.reasoning}")
            if result.final_output.should_follow_up:
                console.print("\n[yellow]Follow-up Queries:[/yellow]")
                queries = result.final_output.queries[:3]  # Take up to 3 queries
                for i, query in enumerate(queries, 1):
                    console.print(f"  {i}. {query}")
                result.final_output.queries = queries
            return result.final_output