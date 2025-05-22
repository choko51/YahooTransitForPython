import re
import json
from bs4 import BeautifulSoup, NavigableString

def extract_route_info(route_div):
    """
    個別のルートdiv要素から詳細情報を抽出する関数。
    """
    route_data = {}

    summary_div = route_div.find('div', class_='routeSummary')
    if not summary_div:
        return None

    title_tag = summary_div.find('h2', class_='title')
    route_data['route_id'] = title_tag.get_text(strip=True) if title_tag else None

    # 優先度 (例: [早, 楽, 安])
    priority_tags = summary_div.select('ul.priority li span')
    route_data['priority'] = [p.get_text(strip=True) for p in priority_tags]

    summary_ul = summary_div.find('ul', class_='summary')
    if summary_ul:
        # 時間情報 (出発時刻, 到着時刻, 所要時間, 乗車時間)
        time_li = summary_ul.find('li', class_='time')
        if time_li:
            dep_arr_span = time_li.find('span', recursive=False) 
            if dep_arr_span:
                dep_time_str = ""
                for content_part in dep_arr_span.contents:
                    if isinstance(content_part, NavigableString):
                        dep_time_str = content_part.strip()
                        if dep_time_str: break
                route_data['departure_time'] = dep_time_str.replace('発→', '').strip() if dep_time_str else None
                
                arr_time_span_mark = dep_arr_span.find('span', class_='mark')
                route_data['arrival_time'] = arr_time_span_mark.get_text(strip=True).replace('着', '').strip() if arr_time_span_mark else None

            time_elements = []
            start_collecting = False
            for child in time_li.children:
                if child == dep_arr_span:
                    start_collecting = True 
                    continue
                if start_collecting:
                    if isinstance(child, NavigableString):
                        cleaned_text = re.sub(r'<!--.*?-->', '', str(child)).strip()
                        if cleaned_text:
                            time_elements.append(cleaned_text)
            
            time_details_text = "".join(time_elements)
            time_match = re.search(r'(\d+分)（乗車(\d+分)）', time_details_text)
            if time_match:
                route_data['total_time'] = time_match.group(1)
                route_data['time_on_board'] = time_match.group(2)
            elif '分' in time_details_text:
                route_data['total_time'] = time_details_text.strip()

                route_data['time_on_board'] = time_details_text.strip() if '（乗車' not in time_details_text else None
            else:
                route_data['total_time'] = None
                route_data['time_on_board'] = None


        # 乗り換え回数
        transfers_li = summary_ul.find('li', class_='transfer')
        if transfers_li and transfers_li.find('span', class_='mark'):
            route_data['transfers'] = transfers_li.find('span', class_='mark').get_text(strip=True) + "回"

        # 料金
        fare_li = summary_ul.find('li', class_='fare')
        if fare_li and fare_li.find('span', class_='mark'):
            route_data['fare'] = fare_li.find('span', class_='mark').get_text(strip=True) + "円"
            # 料金タイプ (IC優先など)
            fare_type_span = fare_li.find('span', class_=lambda x: x != 'mark' and x != 'icnIc') 
            if fare_type_span:
                route_data['fare_type'] = fare_type_span.get_text(strip=True)
            elif fare_li.find('span', class_='icnIc'): 
                if len(fare_li.contents) > 1 and isinstance(fare_li.contents[1], NavigableString):
                    route_data['fare_type'] = fare_li.contents[1].strip()
                elif len(fare_li.contents) > 1 and fare_li.contents[1].name == 'span':
                    route_data['fare_type'] = fare_li.contents[1].get_text(strip=True)


        # 距離
        distance_li = summary_ul.find('li', class_='distance')
        if distance_li:
            route_data['distance'] = distance_li.get_text(strip=True)

    # --- ルート詳細 ---
    route_details_div = route_div.find('div', class_='routeDetail')
    details = []
    if route_details_div:
        elements = route_details_div.find_all(lambda tag: tag.name == 'div' and ('station' in tag.get('class', []) or 'fareSection' in tag.get('class', [])), recursive=False)
        
        for elem in elements:
            if 'station' in elem.get('class', []):
                station_type = 'departure_station' if elem.find('span', class_='icnStaDep') else 'arrival_station'
                time_tag = elem.find('ul', class_='time').find('li') if elem.find('ul', class_='time') else None
                station_name_tag = elem.find('dl').find('dt').find('a') if elem.find('dl') and elem.find('dl').find('dt') else None
                details.append({
                    'type': station_type,
                    'time': time_tag.get_text(strip=True) if time_tag else None,
                    'station_name': station_name_tag.get_text(strip=True) if station_name_tag else None
                })
            elif 'fareSection' in elem.get('class', []):
                transport_info = {'type': 'transport'}
                access_div = elem.find('div', class_='access')
                if access_div:
                    transport_li = access_div.find('li', class_='transport')
                    if transport_li:
                        line_div = transport_li.find('div')
                        if line_div:
                            # 路線名 (アイコンの後のテキストノード)
                            line_name_candidate = ""
                            for content in line_div.contents:
                                if isinstance(content, NavigableString):
                                    line_name_candidate = content.strip()
                                    if line_name_candidate: # 最初の空でないテキストノード
                                        break
                            transport_info['line_name'] = line_name_candidate
                            
                            destination_span = line_div.find('span', class_='destination')
                            if destination_span:
                                full_dest_text = destination_span.get_text(strip=True)
                                first_train_icon = destination_span.find('span', class_='icnFirstTrain')
                                transport_info['is_first_train'] = bool(first_train_icon)
                                if transport_info['is_first_train'] and first_train_icon:
                                    first_train_text = first_train_icon.get_text(strip=True)
                                    transport_info['destination'] = full_dest_text.replace(first_train_text, "").strip()
                                else:
                                    transport_info['destination'] = full_dest_text
                            else:
                                transport_info['destination'] = None
                                transport_info['is_first_train'] = False
                    
                    platform_li = access_div.find('li', class_='platform')
                    if platform_li:
                        platform_text = platform_li.get_text(strip=True, separator=' ')
                        dep_match = re.search(r'\[発\]\s*([^→]+?)(?:\s*→|$)', platform_text)
                        arr_match = re.search(r'→\s*\[着\]\s*(.+)', platform_text)
                        transport_info['departure_platform'] = dep_match.group(1).strip() if dep_match else None
                        transport_info['arrival_platform'] = arr_match.group(1).strip() if arr_match else None
                    
                    fare_p = elem.find('p', class_='fare')
                    if fare_p and fare_p.find('span'):
                        transport_info['fare_segment'] = fare_p.find('span').get_text(strip=True) + "円"
                details.append(transport_info)
    
    route_data['details'] = details
    return route_data

def extract_routes_from_html(html_content):
    """
    HTMLコンテンツから全てのルート情報を抽出しリストとして返す関数。
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    all_routes_data = []
    
    # ルート詳細の親コンテナを探す
    route_container = soup.find('div', id='srline', class_='elmRouteDetail')
    if not route_container:
        # Next.jsの構造からデータを取得しようと試みる (フォールバック)
        script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')
        if script_tag:
            print("Note: Parsing data from __NEXT_DATA__ JSON as #srline was not found directly.")
            try:
                next_data = json.loads(script_tag.string)
                features = next_data.get('props', {}).get('pageProps', {}).get('naviSearchParam', {}).get('featureInfoList', [])
                return [] 
            except json.JSONDecodeError:
                print("Error decoding __NEXT_DATA__ JSON.")
                return []
        print("Route container (#srline) not found in HTML.")
        return []

    # idが "route" で始まり数字が続くdiv要素を抽出 (例: route01, route02)
    route_divs = route_container.find_all('div', id=re.compile(r'^route\d+$'), recursive=False)
    
    if not route_divs:
        print("No route divs (e.g., #route01) found within #srline.")
        return []

    for r_div in route_divs:
        extracted_info = extract_route_info(r_div)
        if extracted_info:
            all_routes_data.append(extracted_info)
            
    return all_routes_data