from common.logger import get_logger

logger = get_logger(__name__)

class SEOOptimizer:
    def optimize(self, metadata: dict) -> dict:
        logger.info("[SEOOptimizer] Validating and optimizing metadata constraints...")
        
        # 1. Title Length Constraint
        title = metadata.get("title", "")
        if len(title) > 100:
            logger.warning("Title exceeds 100 characters. Truncating.")
            metadata["title"] = title[:97] + "..."
            
        # 2. Description Length Constraint
        desc = metadata.get("description", "")
        if len(desc) > 5000:
            logger.warning("Description exceeds 5000 characters. Truncating.")
            metadata["description"] = desc[:4997] + "..."
            
        # 3. Tags constraint
        tags = metadata.get("tags", [])
        # YouTube limits total tags length to 500 chars roughly.
        valid_tags = []
        current_len = 0
        for tag in tags:
            if current_len + len(tag) + 1 <= 400: # Safe limit
                valid_tags.append(tag)
                current_len += len(tag) + 1
        metadata["tags"] = valid_tags
        
        logger.info("[SEOOptimizer] Metadata passed SEO validation.")
        return metadata
