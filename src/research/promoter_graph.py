"""
src/research/promoter_graph.py

Uses NetworkX to build and analyze promoter/director relationships
to detect cross-holdings, shell companies, or related party risks.
"""
import logging
import networkx as nx
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class PromoterGraph:
    """Builds and analyzes a graph of directors and their associated companies."""

    def __init__(self):
        self.graph = nx.Graph()

    def build_from_mca_data(self, main_company: str, directors: List[Dict[str, str]]):
        """
        Populate graph with promoters and their other directorships.
        directors = [{"name": "Rahul", "other_companies": ["Comp A", "Comp B"]}]
        """
        self.graph.add_node(main_company, type="target_company")
        
        for d in directors:
            d_name = d.get("name")
            self.graph.add_node(d_name, type="director")
            self.graph.add_edge(main_company, d_name, relationship="director_of")
            
            for oc in d.get("other_companies", []):
                self.graph.add_node(oc, type="associated_company")
                self.graph.add_edge(d_name, oc, relationship="director_of")

    def detect_shell_company_risk(self) -> Dict[str, Any]:
        """
        A heuristic: If a director is on the board of > 15 companies, 
        it's a massive red flag for shell company networks in India.
        """
        high_risk_directors = []
        
        for node, data in self.graph.nodes(data=True):
            if data.get("type") == "director":
                degree = self.graph.degree(node)
                if degree > 10:  # Threshold for warning
                    high_risk_directors.append(node)
                    
        return {
            "shell_company_risk": len(high_risk_directors) > 0,
            "high_risk_directors": high_risk_directors,
            "total_associated_companies": len([n for n, d in self.graph.nodes(data=True) if d.get('type') == 'associated_company'])
        }
