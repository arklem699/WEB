from django.shortcuts import render

data = [
            {'date': '12.10.2023', 'time': '13:00', 'name': 'Ольгина А.С.', 'id': 1},
            {'date': '13.10.2023', 'time': '14:00', 'name': 'Иванов А.А.', 'id': 2},
            {'date': '13.10.2023', 'time': '15:00', 'name': 'Мирошкина Д.С.', 'id': 3},
        ]

def GetOrders(request):
    return render(request, 'orders.html', {'data' : data })

def GetOrder(request, id):
    for my_dict in data:
        if my_dict['id'] == id:
            return render(request, 'order.html', {'data': my_dict})

def GetQuery(request):
    query = request.GET.get('query', '')
    new_data = []
    for item in data:
        if query in item["date"]:
            new_data.append(item)
    return render(request, 'orders.html', {'data': new_data})