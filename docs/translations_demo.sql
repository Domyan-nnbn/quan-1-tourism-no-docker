-- Optional: populate missing zh/fr/ja on UNEDITED original demo scripts only.

-- Run migrate_5_languages.sql first. This script preserves custom scripts/translations.

BEGIN;

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '滨城市场是胡志明市中心一个熟悉的旅游目的地。您可以浏览当地摊位，品尝特色食品。购物前请先询问价格，在人多的地方注意保管个人物品。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'Le marché de Ben Thanh est une destination bien connue du centre de Hô Chi Minh-Ville. Découvrez les étals et la cuisine locale. Demandez les prix avant d’acheter et gardez vos affaires près de vous dans les endroits fréquentés.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN 'ベンタイン市場は、ホーチミン市中心部のよく知られた観光スポットです。地元の店や食べ物を楽しめます。購入する前に値段を確認し、混雑した場所では持ち物に注意してください。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Chợ Bến Thành'
AND c.source->>'type'='demo_original' AND c.vi='Chợ Bến Thành là một địa điểm quen thuộc ở trung tâm Thành phố Hồ Chí Minh. Bạn có thể khám phá các gian hàng và món ăn địa phương. Hãy hỏi giá trước khi mua và giữ tư trang khi đi trong khu vực đông người.' AND c.en='Ben Thanh Market is a familiar destination in central Ho Chi Minh City. Explore local stalls and food. Ask for prices before buying and keep your belongings close in crowded areas.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '统一宫是市中心的一处历史景点。建筑和展览室帮助游客了解越南的一段历史。参观前请在入口处确认最新的开放时间和门票信息。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'Le palais de l’Indépendance est un site historique du centre-ville. Son architecture et ses salles d’exposition présentent une période de l’histoire vietnamienne. Vérifiez les horaires et les conditions d’entrée sur place.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN '統一会堂は市中心部にある歴史的な観光施設です。建築や展示室を通して、ベトナムの歴史の一時期を知ることができます。入場前に営業時間とチケット情報を確認してください。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Dinh Độc Lập'
AND c.source->>'type'='demo_original' AND c.vi='Dinh Độc Lập là một điểm tham quan lịch sử tại trung tâm thành phố. Không gian kiến trúc và các phòng trưng bày giúp du khách tìm hiểu về một giai đoạn lịch sử Việt Nam. Kiểm tra thông tin mở cửa và vé tại quầy trước khi tham quan.' AND c.en='Independence Palace is a historical attraction in the city centre. Its architecture and exhibition rooms introduce a period of Vietnamese history. Check current opening hours and admission details at the entrance.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '西贡圣母大教堂位于巴黎公社广场附近，是城市中醒目的建筑地标。请在允许进入的区域欣赏建筑，并尊重宗教空间和维修围栏。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'La cathédrale Notre-Dame se trouve près de la place de la Commune de Paris. C’est un repère architectural important. Admirez-la depuis les zones autorisées et respectez le lieu religieux ainsi que les barrières de travaux.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN 'サイゴン大教会はパリ・コミューン広場にある、街を代表する建築です。見学が許可された場所から眺め、宗教施設や修復作業の柵を尊重してください。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Nhà thờ Đức Bà'
AND c.source->>'type'='demo_original' AND c.vi='Nhà thờ Đức Bà nằm ở khu vực Công xã Paris. Công trình là một dấu mốc kiến trúc nổi bật của thành phố. Hãy quan sát từ khu vực được phép và tôn trọng không gian tôn giáo cũng như các rào chắn bảo trì.' AND c.en='Notre Dame Cathedral stands at Paris Commune Square. It is a prominent architectural landmark. Observe it from permitted areas and respect the religious space and any maintenance barriers.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '中央邮局位于圣母大教堂附近。允许进入时，不妨欣赏建筑外观和内部空间。这里也可以让您了解邮政服务。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'La poste centrale se situe près de la cathédrale Notre-Dame. Prenez le temps d’observer sa façade et son intérieur lorsque l’accès est autorisé. Le bâtiment permet aussi de découvrir les services postaux.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN '中央郵便局はサイゴン大教会の近くにあります。入場できる場合は、外観や内部の空間をゆっくり見学してください。郵便の業務についても知ることができます。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Bưu điện Thành phố'
AND c.source->>'type'='demo_original' AND c.vi='Bưu điện Thành phố là một điểm dừng gần Nhà thờ Đức Bà. Hãy dành thời gian quan sát mặt tiền và không gian bên trong khi được phép vào. Đây cũng là nơi bạn có thể tìm hiểu về hoạt động bưu chính.' AND c.en='The Central Post Office is a stop near Notre Dame Cathedral. Take time to observe its facade and interior when access is available. The building also offers an introduction to postal services.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '市立歌剧院位于蓝山广场附近。建筑前方是欣赏外观的好地方。若想观看演出，请向主办方查询节目安排和门票。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'L’opéra municipal se trouve près de la place Lam Son. Son parvis permet d’admirer l’architecture. Pour assister à un spectacle, consultez le programme et les billets auprès de l’organisateur.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN '市民劇場はラムソン広場に面しています。建物の前から美しい建築を眺められます。公演を観たい場合は、主催者の案内で日程とチケットを確認してください。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Nhà hát Thành phố'
AND c.source->>'type'='demo_original' AND c.vi='Nhà hát Thành phố nằm ở khu vực Công trường Lam Sơn. Không gian phía trước phù hợp để ngắm kiến trúc và chụp ảnh từ nơi được phép. Nếu muốn xem biểu diễn, hãy kiểm tra lịch và vé của đơn vị tổ chức.' AND c.en='The City Opera House stands by Lam Son Square. The area in front offers views of its architecture. For performances, check the programme and tickets with the organiser.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '阮惠步行街是市中心的公共空间。您可以散步，感受城市生活。穿越路口时请注意车辆，并保持环境整洁。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'La rue piétonne Nguyen Hue est un espace public du centre-ville. Promenez-vous et observez la vie urbaine. Faites attention aux véhicules aux intersections et veillez à la propreté des lieux.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN 'グエンフエ歩行者通りは市中心部の公共スペースです。散歩をしながら街の暮らしを感じられます。交差点では車に注意し、周辺を清潔に保ちましょう。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Phố đi bộ Nguyễn Huệ'
AND c.source->>'type'='demo_original' AND c.vi='Phố đi bộ Nguyễn Huệ là không gian công cộng ở trung tâm thành phố. Bạn có thể đi dạo và quan sát nhịp sống đô thị. Hãy chú ý phương tiện ở các giao lộ và giữ gìn vệ sinh khu vực.' AND c.en='Nguyen Hue Walking Street is a public space in the city centre. Enjoy a walk and observe urban life. Watch for traffic at intersections and help keep the area clean.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '市政厅位于阮惠街的一端。游客可从前方公共区域欣赏建筑。这里是行政机关，内部参观须遵守具体规定和活动安排。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'L’hôtel de ville se trouve à une extrémité de la rue Nguyen Hue. Admirez son architecture depuis l’espace public devant le bâtiment. L’accès intérieur dépend des règles et des programmes de visite de cette administration.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN '市庁舎はグエンフエ通りの一端にあります。建物の前の公共スペースから建築を眺められます。行政機関のため、内部の見学は規則や特別な見学プログラムによります。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Trụ sở UBND Thành phố'
AND c.source->>'type'='demo_original' AND c.vi='Trụ sở Ủy ban nhân dân Thành phố nằm ở đầu đường Nguyễn Huệ. Bạn có thể quan sát kiến trúc từ không gian công cộng phía trước. Đây là cơ quan hành chính, vì vậy việc tham quan bên trong phụ thuộc quy định và chương trình cụ thể.' AND c.en='City Hall stands at one end of Nguyen Hue Street. View its architecture from the public area in front. As an administrative building, interior access depends on specific rules and programmes.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '美术馆适合喜爱艺术的游客。参观时请阅读作品旁的说明，并遵守拍照规定。开放时间和票价请以官方信息为准。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'Le musée des Beaux-Arts est une destination pour les amateurs d’art. Lisez les notices des œuvres et respectez les règles de photographie. Consultez les informations officielles pour les horaires et les tarifs.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN '美術館は芸術に興味がある方におすすめの場所です。作品の説明を読み、写真撮影の規則に従ってください。開館時間や入場料は公式情報で確認しましょう。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Bảo tàng Mỹ thuật'
AND c.source->>'type'='demo_original' AND c.vi='Bảo tàng Mỹ thuật là điểm đến dành cho người yêu nghệ thuật. Khi tham quan, hãy đọc thông tin bên cạnh tác phẩm và tuân thủ hướng dẫn về chụp ảnh. Kiểm tra giờ mở cửa và giá vé tại nguồn chính thức.' AND c.en='The Fine Arts Museum is a destination for art lovers. Read the labels beside works and follow photography rules. Check official information for current opening hours and admission prices.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '白藤码头是沿河散步和欣赏景色的地方。请沿步行道行走，与水边保持安全距离，并爱护公共环境。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'Le quai Bach Dang est un lieu de promenade au bord de la rivière. Restez sur les chemins piétons, gardez une distance de sécurité avec l’eau et respectez le paysage partagé.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN 'バクダン埠頭は川沿いの散歩や景色を楽しめる場所です。歩行者用の道を利用し、水際から安全な距離を保ち、周囲の環境を大切にしてください。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Bến Bạch Đằng'
AND c.source->>'type'='demo_original' AND c.vi='Bến Bạch Đằng là khu vực ven sông để đi dạo và ngắm cảnh. Hãy đi trên lối dành cho người đi bộ, tránh sát mép nước và giữ gìn cảnh quan chung.' AND c.en='Bach Dang Wharf is a riverside area for walking and enjoying the view. Stay on pedestrian paths, keep a safe distance from the water and respect the shared landscape.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '西贡动植物园有绿地和动物展示区域。请遵守各区域的指示，不要擅自喂食动物，也不要翻越围栏。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'Le zoo et jardin botanique de Saïgon propose des espaces verts et des enclos animaliers. Suivez les consignes, ne nourrissez pas les animaux sans autorisation et restez derrière les barrières.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN 'サイゴン動植物園には緑豊かな空間と動物の展示エリアがあります。各場所の案内に従い、許可なく動物に餌を与えたり、柵を越えたりしないでください。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Thảo Cầm Viên'
AND c.source->>'type'='demo_original' AND c.vi='Thảo Cầm Viên có không gian cây xanh và khu nuôi động vật. Hãy tuân thủ hướng dẫn tại từng khu vực, không cho động vật ăn tùy ý và không vượt hàng rào.' AND c.en='Saigon Zoo and Botanical Gardens offers green spaces and animal enclosures. Follow signs, do not feed animals without permission and remain behind barriers.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '历史博物馆通过文物和展览介绍过去。建议按展厅顺序参观，并留出时间阅读介绍资料，以便理解展览内容。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'Le musée d’Histoire présente le passé à travers des objets et des expositions. Suivez l’ordre des salles et prenez le temps de lire les panneaux de présentation pour mieux comprendre le parcours.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN '歴史博物館では、資料や展示を通して過去を学べます。展示室の順路に沿って進み、紹介文を読む時間を取ると、内容をより理解しやすくなります。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Bảo tàng Lịch sử'
AND c.source->>'type'='demo_original' AND c.vi='Bảo tàng Lịch sử là nơi tìm hiểu quá khứ qua hiện vật và trưng bày. Bạn nên đi theo trình tự các phòng để nắm được nội dung và dành thời gian đọc phần giới thiệu.' AND c.en='The History Museum introduces the past through artefacts and exhibitions. Follow the room sequence and take time to read the introductory displays.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '城市博物馆介绍当地历史和城市生活的不同方面。请在入口查看参观指引，并与展品保持适当距离。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'Le musée de la ville présente plusieurs aspects de l’histoire locale et de la vie urbaine. Consultez les consignes à l’entrée et gardez une distance respectueuse avec les objets exposés.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN '市立博物館は、地元の歴史や都市生活のさまざまな側面を紹介しています。入口で見学の案内を確認し、展示品には近づきすぎないようにしてください。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Bảo tàng Thành phố'
AND c.source->>'type'='demo_original' AND c.vi='Bảo tàng Thành phố giới thiệu nhiều khía cạnh lịch sử và đời sống đô thị. Hãy kiểm tra hướng dẫn tham quan tại lối vào và giữ khoảng cách với hiện vật.' AND c.en='The City Museum introduces aspects of local history and urban life. Check visitor guidance at the entrance and keep a respectful distance from the exhibits.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '阮文平书街是阅读和文化活动的空间。您可以逛书店，寻找喜欢的书，也可以在适合休息的地方稍作停留。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'La rue du livre Nguyen Van Binh est consacrée aux livres et aux activités culturelles. Parcourez les librairies, trouvez un ouvrage qui vous plaît et profitez d’une pause dans un endroit adapté.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN 'グエンヴァンビン書店通りは、本や文化活動を楽しむ場所です。書店を巡ってお気に入りの一冊を探し、適切な場所でひと休みすることもできます。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Đường sách Nguyễn Văn Bình'
AND c.source->>'type'='demo_original' AND c.vi='Đường sách Nguyễn Văn Bình là không gian dành cho sách và hoạt động văn hóa. Bạn có thể dạo quanh các gian sách, tìm một cuốn sách yêu thích và nghỉ chân tại khu vực phù hợp.' AND c.en='Nguyen Van Binh Book Street is a space for books and cultural activities. Browse the bookshops, discover a favourite title and enjoy a pause in the city.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '比特克斯科金融塔是城市天际线中容易辨认的高层建筑。您可以从周边区域欣赏它。楼内设施可能有各自的入场规定和收费。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'La tour Bitexco est un immeuble reconnaissable dans la silhouette de la ville. Admirez-la depuis les environs. Les services à l’intérieur peuvent avoir leurs propres règles d’accès et tarifs.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN 'ビテクスコ・フィナンシャルタワーは、街の景観の中で目立つ高層建築です。周辺から外観を眺められます。内部の各施設には、それぞれの利用規則や料金があります。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Bitexco Financial Tower'
AND c.source->>'type'='demo_original' AND c.vi='Bitexco là một công trình cao tầng dễ nhận ra trong đường chân trời thành phố. Bạn có thể quan sát từ khu vực xung quanh. Các dịch vụ bên trong có quy định và giá vé riêng.' AND c.en='Bitexco is a recognisable high-rise on the city skyline. View it from the surrounding area. Facilities inside may have separate access rules and admission charges.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '陶坛公园是城市中的绿色空间。沿步道漫步，享受树荫，并与在此锻炼的居民友好地共享空间。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'Le parc Tao Dan est un espace vert au cœur de la ville. Suivez les allées, profitez de l’ombre des arbres et partagez les lieux avec les habitants qui viennent faire de l’exercice.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN 'タオダン公園は都市の中にある緑の空間です。遊歩道を歩き、木陰を楽しみながら、運動する地元の人たちと気持ちよく場所を共有してください。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Công viên Tao Đàn'
AND c.source->>'type'='demo_original' AND c.vi='Công viên Tao Đàn là khoảng xanh giữa đô thị. Hãy đi trên các lối dạo, tận hưởng bóng cây và chia sẻ không gian với người dân tập thể dục.' AND c.en='Tao Dan Park is a green space within the city. Follow the walking paths, enjoy the shade and share the space considerately with local residents.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '九月二十三日公园位于范五老区域附近，是游览市中心时休息的地方。请注意现场标识和正在调整的区域。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'Le parc du 23 Septembre se trouve près du quartier Pham Ngu Lao. Il offre une halte pendant la découverte du centre. Respectez les indications et les zones en cours de réaménagement.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN '九月二十三日公園はファングーラオ地区の近くにあり、市中心部を散策する際の休憩場所になります。案内表示や整備中のエリアに注意してください。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Công viên 23 tháng 9'
AND c.source->>'type'='demo_original' AND c.vi='Công viên 23 tháng 9 nằm gần khu vực Phạm Ngũ Lão. Đây là điểm nghỉ chân khi khám phá trung tâm. Hãy chú ý biển hướng dẫn và các khu vực đang được tổ chức lại.' AND c.en='September 23 Park is near the Pham Ngu Lao area. It can provide a break during a city walk. Pay attention to signs and any areas undergoing changes.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '马里安曼寺庙是市中心的一处宗教场所。参观时请穿着得体，轻声交谈，在祭祀区域拍照前先征求许可。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'Le temple Mariamman est un lieu religieux du centre-ville. Portez une tenue respectueuse, parlez doucement et demandez l’autorisation avant de photographier les espaces de culte.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN 'マリアンマン寺院は市中心部にある宗教施設です。礼儀にかなった服装で訪れ、静かに話し、礼拝の場所を撮影する前には許可を求めてください。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Đền Mariamman'
AND c.source->>'type'='demo_original' AND c.vi='Đền Mariamman là một địa điểm tôn giáo ở trung tâm thành phố. Khi ghé thăm, hãy ăn mặc lịch sự, nói nhỏ và xin phép trước khi chụp ảnh trong khu vực thờ tự.' AND c.en='Mariamman Temple is a religious site in the city centre. Dress respectfully, speak quietly and ask before taking photographs in worship areas.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '新定市场让游客了解当地的购物和日常生活。通道可能较拥挤，请注意个人物品，购买前清楚确认价格。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'Le marché de Tan Dinh permet de découvrir les achats et la vie quotidienne locale. Les allées peuvent être fréquentées. Surveillez vos affaires et confirmez clairement les prix avant d’acheter.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN 'タンディン市場では、地元の買い物や日常生活の様子を知ることができます。通路は混雑することがあるので、持ち物に注意し、購入前に値段をはっきり確認してください。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Chợ Tân Định'
AND c.source->>'type'='demo_original' AND c.vi='Chợ Tân Định là nơi khám phá sinh hoạt mua bán địa phương. Các lối đi có thể đông người, nên hãy chú ý tư trang và hỏi giá rõ ràng khi mua hàng.' AND c.en='Tan Dinh Market offers a look at local shopping and daily life. Aisles can be busy, so keep track of your belongings and confirm prices before buying.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '陈兴道祠是一处纪念和信仰活动的场所。请遵守现场指引，保持安静，并尊重正在举行仪式的人们。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'Le temple Tran Hung Dao est un lieu de mémoire et de pratique religieuse. Suivez les consignes, préservez le calme et respectez les personnes qui participent aux cérémonies.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN 'チャンフンダオ廟は、追悼や信仰のための場所です。現地の案内に従い、静かに過ごし、儀式に参加している人たちを尊重してください。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Đền Trần Hưng Đạo'
AND c.source->>'type'='demo_original' AND c.vi='Đền Trần Hưng Đạo là không gian tưởng niệm và sinh hoạt tín ngưỡng. Hãy tuân thủ hướng dẫn tại chỗ, giữ trật tự và tôn trọng người đang hành lễ.' AND c.en='Tran Hung Dao Temple is a place of remembrance and worship. Follow guidance on site, keep noise low and respect people taking part in ceremonies.';

UPDATE content_versions AS c SET zh=CASE WHEN trim(c.zh)='' THEN '裴援步行街有许多服务和娱乐场所，特别是晚上可能非常热闹、拥挤和嘈杂。请保管好个人物品，并选择适合自己的路线。' ELSE c.zh END,
    fr=CASE WHEN trim(c.fr)='' THEN 'Le quartier Bui Vien propose de nombreux services et lieux de divertissement. Il peut être animé, fréquenté et bruyant, surtout le soir. Gardez vos affaires en sécurité et choisissez un itinéraire qui vous convient.' ELSE c.fr END,
    ja=CASE WHEN trim(c.ja)='' THEN 'ブイビエン通りには多くのサービスや娯楽施設があります。特に夜は混雑し、にぎやかになることがあります。持ち物をしっかり管理し、自分に合った散策ルートを選んでください。' ELSE c.ja END
FROM pois AS p WHERE c.poi_id=p.id AND p.name='Phố đi bộ Bùi Viện'
AND c.source->>'type'='demo_original' AND c.vi='Khu vực Bùi Viện có nhiều hoạt động dịch vụ và giải trí. Không gian có thể đông và ồn, đặc biệt vào buổi tối. Hãy giữ tư trang và cân nhắc lộ trình phù hợp với mình.' AND c.en='Bui Vien is known for services and entertainment. It can be crowded and noisy, particularly in the evening. Keep your belongings secure and choose a route that suits you.';

COMMIT;