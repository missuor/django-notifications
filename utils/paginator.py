# coding=utf-8
from django.core.paginator import (
    EmptyPage,
    PageNotAnInteger,
    Page as DefaultPage,
    Paginator as DefaultPaginator
)


class Paginator(DefaultPaginator):

    def _get_page(self, *args, **kwargs):
        """
        Return an instance of a single page.

        This hook can be used by subclasses to use an alternative to the
        standard :cls:`Page` object.
        """
        return Page(*args, **kwargs)

    def _get_page_info(self, *args, **kwargs):
        """Return page info"""
        return {
            'count': self.count,  # 条目总数
            'num_pages': self.num_pages,  # 页数
        }
    page_info = property(_get_page_info)


class Page(DefaultPage):

    def to_dict(self):
        objs = self.object_list
        return [hasattr(o, 'to_dict') and o.to_dict() or o for o in objs]


def paginator(request, objs, **kw):
    p = Paginator(objs, 5)
    page_info = p.page_info

    page = request.GET.get('p')
    try:
        paged_objs = p.page(page)
    except PageNotAnInteger:
        page = 1
        paged_objs = p.page(1)
    except EmptyPage:
        page = p.num_pages
        paged_objs = p.page(p.num_pages)
    page_info.update({'number': page})

    return paged_objs, page_info
