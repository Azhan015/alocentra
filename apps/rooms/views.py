from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.accounts.utils import permission_required_custom, get_user_permissions
from .models import Room
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
import json

@login_required
@permission_required_custom('can_view_rooms')
def rooms_view(request):
    permissions = get_user_permissions(request.user)
    rooms_list = Room.objects.filter(is_active=True).order_by('room_no')
    paginator = Paginator(rooms_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'permissions': permissions,
        'page_obj': page_obj,
        'room_count': rooms_list.count(),
    }
    return render(request, 'rooms/rooms.html', context)

@login_required
@permission_required_custom('can_add_rooms')
@require_POST
def add_room(request):
    try:
        room_no = request.POST.get('room_no')
        capacity = request.POST.get('capacity')
        if not room_no or not capacity:
            return JsonResponse({'success': False, 'message': 'Missing fields'})
        
        if Room.objects.filter(room_no=room_no, is_active=True).exists():
            return JsonResponse({'success': False, 'message': 'Room already exists'})
            
        room = Room.objects.create(room_no=room_no, capacity=capacity, created_by=request.user)
        return JsonResponse({'success': True, 'message': 'Room added successfully', 'data': {'id': room.id, 'room_no': room.room_no, 'capacity': room.capacity}})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@permission_required_custom('can_add_rooms')
def edit_room(request, id):
    room = get_object_or_404(Room, id=id, is_active=True)
    if request.method == 'GET':
        return JsonResponse({'room_no': room.room_no, 'capacity': room.capacity})
    elif request.method == 'POST':
        room_no = request.POST.get('room_no')
        capacity = request.POST.get('capacity')
        if Room.objects.filter(room_no=room_no, is_active=True).exclude(id=room.id).exists():
            return JsonResponse({'success': False, 'message': 'Room number already exists'})
        room.room_no = room_no
        room.capacity = capacity
        room.save()
        return JsonResponse({'success': True, 'message': 'Room updated', 'data': {'id': room.id, 'room_no': room.room_no, 'capacity': room.capacity}})

@login_required
@permission_required_custom('can_delete_rooms')
@require_POST
def delete_room(request, id):
    room = get_object_or_404(Room, id=id)
    room.is_active = False
    room.save()
    return JsonResponse({'success': True, 'message': 'Room deleted'})

@login_required
@permission_required_custom('can_delete_rooms')
@require_POST
def bulk_delete_rooms(request):
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        Room.objects.filter(id__in=ids).update(is_active=False)
        return JsonResponse({'success': True, 'message': f'{len(ids)} rooms deleted'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@permission_required_custom('can_add_rooms')
@require_POST
def import_rooms(request):
    try:
        data = json.loads(request.body)
        rooms_data = data.get('rooms', [])
        imported = 0
        skipped = 0
        errors = []
        for r in rooms_data:
            room_no = str(r.get('room_no')).strip()
            capacity = r.get('capacity')
            if not room_no or not capacity:
                continue
            if Room.objects.filter(room_no=room_no, is_active=True).exists():
                skipped += 1
            else:
                Room.objects.create(room_no=room_no, capacity=capacity, created_by=request.user)
                imported += 1
        return JsonResponse({'success': True, 'message': f'Successfully imported {imported} rooms. {skipped} duplicates skipped.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
