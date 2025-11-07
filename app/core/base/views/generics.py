from django.views.generic import ListView
from django.http import JsonResponse
from django.db.models import Q
import math

class BaseListView(ListView):
    search_fields = ["",]
    numeric_fields = ["id", ]
    default_order_fields = ["id"]

    def handle_search(self, request, queryset=None):
        try:
            start = int(request.POST.get("start", 0))
            length = int(request.POST.get("length", 10))
            search = request.POST.get("search[value]", "").strip()
            order_fields = self.get_ordering()

            queryset = queryset or self.get_queryset()
            queryset = queryset.order_by(*order_fields)

            if search:
                queryset = self.apply_search_filter(queryset, search)

            total = queryset.count()
            paginated_qs = queryset[start:] if length == -1 else queryset[start:start + length]

            data = [obj.toJSON() for obj in paginated_qs]

            return JsonResponse({
                "data": data,
                "page": math.ceil(start / length) + 1 if length else 1,
                "per_page": length,
                "recordsTotal": total,
                "recordsFiltered": total,
            }, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def get_ordering(self):
        request = self.request
        ordering = []
        for i in range(9):
            col_key = f"order[{i}][column]"
            dir_key = f"order[{i}][dir]"
            if col_key in request.POST:
                col_index = request.POST[col_key]
                field = request.POST.get(f"columns[{col_index}][data]", "").split(".")[0]
                direction = request.POST.get(dir_key, "asc")
                ordering.append(f"-{field}" if direction == "desc" else field)
        return ordering or self.default_order_fields


    def apply_search_filter(self, queryset, search):
        if search.isnumeric():
            q_numeric = Q()
            for field in self.numeric_fields:
                q_numeric |= Q(**{f"{field}__exact": search})
            return queryset.filter(q_numeric)

        q_text = Q()
        for field in self.search_fields:
            q_text |= Q(**{f"{field}__icontains": search})
        return queryset.filter(q_text).exclude(activo=False)
