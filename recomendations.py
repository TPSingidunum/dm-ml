from database import db
from typing import List, Dict
from collections import defaultdict 

class RecommendationEngine:

    def __init__(self):
        self.db = db


    def _get_product_details(self, product_id: int) -> Dict:
        query = """
            SELECT p.product_id, p.name, p.slug, p.description, p.img_url, p.category_id, p.seo_id, p.created_at, p.updated_at
            FROM product as p
            LEFT JOIN category as c ON p.category_id = c.category_id
            WHERE  p.product_id= %s;
        """

        results = self.db.execute_query(query, (product_id,))
        return results[0] if results else None


    def get_recommendations(self, product_id: int, limit: int = 5) -> List[Dict]:
        try:
            target_product = self._get_product_details(product_id)

            collaborative_recs = self.get_collaborative_recommendations(product_id)
            category_recs = self._get_category_recommendations(target_product['category_id'], product_id)

            recommendation_scores = defaultdict(float)
            for product, score in collaborative_recs:
                recommendation_scores[product] += score * 2.0

            for product in category_recs:
                recommendation_scores[product] += 0.5

            sorted_recommendations = sorted(
                recommendation_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]

            recommended_products = []
            for product_id, score in sorted_recommendations:
                product_details = self._get_product_details(product_id)
                product_details['recommendation_score'] = round(score, 2)
                recommended_products.append(product_details)

            return recommended_products
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []

    def _get_category_recommendations(self, category_id: int, exclude_product_id: int) -> List[int]:
        query = """
            SELECT product_id
            FROM product
            WHERE category_id = %s AND product_id != %s
            LIMIT 20;
        """
        results = self.db.execute_query(query, (category_id, exclude_product_id))
        return [r['product_id'] for r in results]

    def get_collaborative_recommendations(self, product_id: int) -> List[tuple]:
        event_weights = {
            'view': 1.0,
            'add_to_cart': 3.0,
            'purchase': 5.0
        }

        query = """
        SELECT DISTINCT user_session
        FROM event
        WHERE product_id = %s
        AND user_session IS NOT NULL 
        """

        sessions = self.db.execute_query(query, (product_id,))
        sessions_ids = [s['user_session'] for s in sessions]

        if len(sessions_ids) == 0:
            return []
        
        placeholders = ','.join(['%s'] * len(sessions_ids))
        query = f"""
        SELECT
            product_id,
            event_type,
            COUNT(*) as interaction_count
        FROM event
        WHERE user_session IN ({placeholders})
        AND product_id != %s
        AND product_id IS NOT NULL
        GROUP BY product_id, event_type
        """

        params = tuple(sessions_ids) + (product_id,)
        interactions = self.db.execute_query(query, params)

        product_scores = defaultdict(float)
        for interaction in interactions:
            pid = interaction['product_id']
            event_type = interaction['event_type']
            count = interaction['interaction_count']
            weight = event_weights.get(event_type, 0)
            product_scores[pid] += count * weight
        
        return sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
    
recommendation_engine = RecommendationEngine()