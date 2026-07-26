"""Pagination utilities."""


class PaginationHelper:
    """Helper class for pagination functionality."""

    @staticmethod
    async def paginate(query, page: int = 1, per_page: int = 100):
        """
        Apply pagination to a SQLAlchemy query.

        Args:
            query: SQLAlchemy query object
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            Tuple of (paginated_query, total_count)
        """
        offset = (page - 1) * per_page

        # Get total count
        total_query = query.statement.compile()
        total_query = select(select_(func.count()).select_from(subquery(total_query)))
        # This is a placeholder - actual implementation would depend on DB type
        total_count = await db.scalar(total_query)

        # Apply pagination
        paginated_query = query.offset(offset).limit(per_page)

        return paginated_query, total_count

    @staticmethod
    def get_pagination_header(page: int, per_page: int, total_count: int):
        """
        Generate pagination headers for API responses.

        Args:
            page: Current page number
            per_page: Items per page
            total_count: Total number of items

        Returns:
            Dictionary with pagination metadata
        """
        total_pages = (total_count + per_page - 1) // per_page

        return {
            "page": page,
            "per_page": per_page,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_previous": page > 1,
            "has_next": page < total_pages,
        }