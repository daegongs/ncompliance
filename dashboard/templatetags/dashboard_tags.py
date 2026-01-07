"""
대시보드 커스텀 템플릿 태그 및 필터
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    딕셔너리에서 키로 값을 가져오는 필터
    사용법: {{ my_dict|get_item:key }}
    """
    if dictionary is None:
        return None
    
    if isinstance(dictionary, dict):
        item = dictionary.get(key)
        if isinstance(item, dict):
            return item.get('label', key)
        return item
    
    return None


@register.filter
def get_label(dictionary, key):
    """
    딕셔너리에서 라벨을 가져오는 필터
    사용법: {{ category_labels|get_label:stat.category }}
    """
    if dictionary is None:
        return key
    
    if isinstance(dictionary, dict):
        item = dictionary.get(key)
        if isinstance(item, dict):
            return item.get('label', key)
        return item if item else key
    
    return key






