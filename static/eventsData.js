// MASTER DATABASE: 10+ CARDS PER GENRE (80 TOTAL + DYNAMIC ADDITIONS)
const eventsDatabase = [
    // 1. MUSIC SHOWS
    { id: 1, cat: 'music', title: 'Karan Aujla — WAVY Tour', venue: 'Dynamic Stadium: Pune', date: 'Sat, 24 Oct', price: 799, banner: 'BESTSELLER', img: '/static/images/karan1.jpeg' },
    { id: 2, cat: 'music', title: 'Indian Ocean Live', venue: 'Phoenix Marketcity: Pune', date: 'Sat, 21 Nov', price: 999, banner: 'PROMOTED', img: '/static/images/indianocean.jpeg' },
    { id: 3, cat: 'music', title: 'Arijit Singh Soulful Night', venue: 'DY Patil Stadium: Mumbai', date: 'Sun, 05 Dec', price: 1499, banner: 'SELLING FAST', img: '/static/images/arjit.jpeg' },
    { id: 4, cat: 'music', title: 'Diljit Dosanjh — Dil-Luminati', venue: 'JLN Stadium: Delhi', date: 'Fri, 18 Dec', price: 1999, banner: 'HOT TICKET', img: '/static/images/diljit.jpeg' },
    { id: 5, cat: 'music', title: 'Sunburn Arena ft. Alan Walker', venue: 'Mahalaxmi Racecourse: Mumbai', date: 'Sat, 28 Dec', price: 1250, banner: 'EDM SPECIAL', img: '/static/images/alan.jpeg' },
    { id: 6, cat: 'music', title: 'Ritviz Live In Concert - Mimmi Album Tour', venue: 'Amanora Mall: Pune', date: 'Sat, 10 Jan', price: 699, img: '/static/images/Ritviz.jpg' },
    { id: 7, cat: 'music', title: 'Prateek Kuhad — Silhouettes Tour', venue: 'EON IT Park: Pune', date: 'Sun, 18 Jan', price: 899, img: 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=600&q=80' },
    { id: 8, cat: 'music', title: 'NH7 Weekender Festival', venue: 'Teerth Fields: Pune', date: 'Fri, 06 Feb', price: 2499, banner: 'FESTIVAL PASS', img: '/static/images/prateek.jpeg' },
    { id: 9, cat: 'music', title: 'When Chai Met Toast Live', venue: 'The Mills: Pune', date: 'Sat, 14 Feb', price: 599, img: '/static/images/chai.jpeg' },
    { id: 10, cat: 'music', title: 'Divine — Punya Paap Experience', venue: 'Gachibowli Stadium: Hyderabad', date: 'Sat, 28 Feb', price: 899, img: '/static/images/divine1.jpeg' },

    // 2. COMEDY SHOWS
    { id: 11, cat: 'comedy', title: 'Anubhav Singh Bassi — Bas Kar Bassi', venue: 'Bal Gandharva: Pune', date: 'Sat, 12 Oct', price: 499, banner: 'HOUSEFULL', img: '/static/images/bassi.jpeg' },
    { id: 12, cat: 'comedy', title: 'Zakir Khan — Tathastu Live', venue: 'Yashwantrao Chavan Center: Mumbai', date: 'Sun, 25 Oct', price: 799, banner: 'POPULAR', img: '/static/images/zakir.jpg' },
    { id: 13, cat: 'comedy', title: 'Samay Raina Unfiltered', venue: 'The Comedy Club: Pune', date: 'Sat, 07 Nov', price: 599, img: '/static/images/samay.jpeg' },
    { id: 14, cat: 'comedy', title: 'Vir Das — Mind Fool Tour', venue: 'JLN Auditorium: Delhi', date: 'Sun, 15 Nov', price: 999, banner: 'INTERNATIONAL', img: '/static/images/vir.jpg' },
    { id: 15, cat: 'comedy', title: 'Gaurav Kapoor Standup Special', venue: 'Classic Rock Coffee Co.: Pune', date: 'Sat, 28 Nov', price: 499, img: '/static/images/kapoor.jpg' },
    { id: 16, cat: 'comedy', title: 'Biswa Kalyan Rath — Into The Oven', venue: 'Bhartiya Vidya Bhavan: Pune', date: 'Fri, 04 Dec', price: 699, img: '/static/images/biswa.jpg' },
    { id: 17, cat: 'comedy', title: 'Kanan Gill — Is This It?', venue: 'Bal Gandharva: Pune', date: 'Sat, 12 Dec', price: 599, img: '/static/images/gill.jpeg' },
    { id: 18, cat: 'comedy', title: 'Harsh Gujral — Jo Bolta Hai Wohi Hota Hai', venue: 'Ram Krishna More Auditorium: Pune', date: 'Sun, 20 Dec', price: 799, banner: 'MUST WATCH', img: '/static/images/harsh.jpeg' },
    { id: 19, cat: 'comedy', title: 'Rahul Subramanian — Crowd Work', venue: 'The Laugh Store: Mumbai', date: 'Sat, 09 Jan', price: 499, img: '/static/images/rahul.jpeg' },
    { id: 20, cat: 'comedy', title: 'Munawar Faruqui Live', venue: 'EON IT Park Auditorium: Pune', date: 'Sat, 23 Jan', price: 699, img: '/static/images/munawar.jpeg' },

    // 3. THEATRE SHOWS
    { id: 21, cat: 'theatre', title: 'Mughal-E-Azam The Musical', venue: 'NCPA: Mumbai', date: 'Fri, 16 Oct', price: 1200, banner: 'GRAND MUSICAL', img: 'https://images.unsplash.com/photo-1460723237483-7a6dc9d0b212?auto=format&fit=crop&w=600&q=80' },
    { id: 22, cat: 'theatre', title: 'AalokNama — Sapno Ka Safar', venue: 'M.E.S. Auditorium: Pune', date: 'Sat, 15 Aug', price: 199, img: 'https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?auto=format&fit=crop&w=600&q=80' },
    { id: 23, cat: 'theatre', title: 'Atrangi Yaari — Storytelling Night', venue: 'The Mic Loft Studio: Pune', date: 'Sat, 01 Aug', price: 250, img: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=600&q=80' },
    { id: 24, cat: 'theatre', title: 'Piya Behrupiya (Twelfth Night)', venue: 'Prithvi Theatre: Mumbai', date: 'Thu, 05 Nov', price: 500, banner: 'CLASSIC', img: 'https://images.unsplash.com/photo-1503095396549-807759245b35?auto=format&fit=crop&w=600&q=80' },
    { id: 25, cat: 'theatre', title: 'Shikhandi — The Story In Between', venue: 'Bal Gandharva: Pune', date: 'Sat, 14 Nov', price: 350, img: 'https://images.unsplash.com/photo-1514306191717-452ec28c7814?auto=format&fit=crop&w=600&q=80' },
    { id: 26, cat: 'theatre', title: 'The Vagina Monologues India', venue: 'St. Andrews Auditorium: Mumbai', date: 'Sun, 22 Nov', price: 600, img: 'https://images.unsplash.com/photo-1478720568477-152d9b164e26?auto=format&fit=crop&w=600&q=80' },
    { id: 27, cat: 'theatre', title: 'Hamlet — Modern Adaptation', venue: 'FTII Main Studio: Pune', date: 'Sat, 05 Dec', price: 300, img: 'https://images.unsplash.com/photo-1460723237483-7a6dc9d0b212?auto=format&fit=crop&w=600&q=80' },
    { id: 28, cat: 'theatre', title: 'Court Martial Drama Play', venue: 'Yashwantrao Chavan Center: Pune', date: 'Sun, 13 Dec', price: 250, img: 'https://images.unsplash.com/photo-1585699324551-f6c309eedeca?auto=format&fit=crop&w=600&q=80' },
    { id: 29, cat: 'theatre', title: 'Ghalib In New Delhi Play', venue: 'Habitat Centre: Delhi', date: 'Sat, 16 Jan', price: 400, img: 'https://images.unsplash.com/photo-1503095396549-807759245b35?auto=format&fit=crop&w=600&q=80' },
    { id: 30, cat: 'theatre', title: 'Charandas Chor Folk Play', venue: 'NCPA Opera House: Mumbai', date: 'Sun, 24 Jan', price: 450, img: 'https://images.unsplash.com/photo-1514306191717-452ec28c7814?auto=format&fit=crop&w=600&q=80' },

    // 4. WORKSHOPS
    { id: 31, cat: 'workshops', title: 'Fluid Art & Resin Coaster Masterclass', venue: 'Mindspace Hub: Pune', date: 'Sat, 10 Oct', price: 1200, banner: 'HANDS-ON', img: 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80' },
    { id: 32, cat: 'workshops', title: 'Sourdough Baking Masterclass', venue: 'The Culinary Studio: Pune', date: 'Sun, 18 Oct', price: 1800, img: 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80' },
    { id: 33, cat: 'workshops', title: 'Terrarium Building & Botanical Art', venue: 'FC Road Social: Pune', date: 'Sat, 24 Oct', price: 950, banner: 'POPULAR', img: 'https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=600&q=80' },
    { id: 34, cat: 'workshops', title: 'Pottery Wheel Throwing Bootcamp', venue: 'Clay Station: Bangalore', date: 'Sat, 07 Nov', price: 1500, img: 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?auto=format&fit=crop&w=600&q=80' },
    { id: 35, cat: 'workshops', title: 'Scented Candle Making Lab', venue: 'Koregaon Park Studio: Pune', date: 'Sun, 15 Nov', price: 850, img: 'https://images.unsplash.com/photo-1603006905003-be475563bc59?auto=format&fit=crop&w=600&q=80' },
    { id: 36, cat: 'workshops', title: 'Smartphone Photography & Editing', venue: 'Viman Nagar Hub: Pune', date: 'Sat, 21 Nov', price: 600, img: 'https://images.unsplash.com/photo-1512790182412-b19e6d62bc39?auto=format&fit=crop&w=600&q=80' },
    { id: 37, cat: 'workshops', title: 'Espresso & Latte Art Brewing', venue: 'Blue Tokai Cafe: Pune', date: 'Sun, 29 Nov', price: 1100, img: 'https://images.unsplash.com/photo-1534778101976-62847782c213?auto=format&fit=crop&w=600&q=80' },
    { id: 38, cat: 'workshops', title: 'Calligraphy & Brush Lettering', venue: 'Baner Art Loft: Pune', date: 'Sat, 05 Dec', price: 750, img: 'https://images.unsplash.com/photo-1516962215378-7fa2e137ae93?auto=format&fit=crop&w=600&q=80' },
    { id: 39, cat: 'workshops', title: 'Cocktail Mixology Masterclass', venue: 'High Spirits Cafe: Pune', date: 'Fri, 11 Dec', price: 2200, banner: 'INCLUDES DRINKS', img: 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&w=600&q=80' },
    { id: 40, cat: 'workshops', title: 'Aromatherapy Soap Making', venue: 'Kothrud Workshop Space: Pune', date: 'Sat, 19 Dec', price: 800, img: 'https://images.unsplash.com/photo-1607006482102-1811a2f6fb39?auto=format&fit=crop&w=600&q=80' },

    // 5. INTERACTIVE GAMES
    { id: 41, cat: 'interactive', title: 'Mystery Room — Escape The Prison', venue: 'Koregaon Park: Pune', date: 'Daily Passes', price: 800, banner: 'TOP RATED', img: 'https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=600&q=80' },
    { id: 42, cat: 'interactive', title: 'Laser Tag Night Arena', venue: 'Phoenix Marketcity: Pune', date: 'Daily Passes', price: 450, img: 'https://images.unsplash.com/photo-1538481199705-c710c4e965fc?auto=format&fit=crop&w=600&q=80' },
    { id: 43, cat: 'interactive', title: 'VR Galaxy Rollercoaster Sim', venue: 'Seasons Mall: Pune', date: 'Daily Passes', price: 350, img: 'https://images.unsplash.com/photo-1622979135225-d2ba269bc1bd?auto=format&fit=crop&w=600&q=80' },
    { id: 44, cat: 'interactive', title: 'Board Game Knights Championship', venue: 'FC Road Cafe: Pune', date: 'Sat, 17 Oct', price: 250, img: 'https://images.unsplash.com/photo-1610890716171-6b1bb98ffd09?auto=format&fit=crop&w=600&q=80' },
    { id: 45, cat: 'interactive', title: 'Glow-in-the-Dark Neon Bowling', venue: 'Smaaash: Pune', date: 'Daily Passes', price: 600, banner: 'NEON PARTY', img: 'https://images.unsplash.com/photo-1538481199705-c710c4e965fc?auto=format&fit=crop&w=600&q=80' },
    { id: 46, cat: 'interactive', title: 'Murder Mystery Dinner Game', venue: 'The Oakwood Hotel: Pune', date: 'Sat, 31 Oct', price: 1500, img: 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=600&q=80' },
    { id: 47, cat: 'interactive', title: 'Paintball Tactical Warfare', venue: 'Xtreme Sports Turf: Pune', date: 'Sat, 07 Nov', price: 700, img: 'https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=600&q=80' },
    { id: 48, cat: 'interactive', title: 'Retro Arcade Tournament (80s Night)', venue: 'Amanora Mall: Pune', date: 'Sun, 15 Nov', price: 400, img: 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80' },
    { id: 49, cat: 'interactive', title: 'Outdoor Treasure Hunt Quest', venue: 'Empress Garden: Pune', date: 'Sun, 22 Nov', price: 500, img: 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=600&q=80' },
    { id: 50, cat: 'interactive', title: 'Smash Room — Rage Relief Arena', venue: 'Baner Arena: Pune', date: 'Daily Passes', price: 900, img: 'https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=600&q=80' },

    // 6. ADVENTURE & FUN
    { id: 51, cat: 'adventure', title: 'Diamond Water Park Day Pass', venue: 'Lohegaon: Pune', date: 'Daily Passes', price: 899, banner: 'BESTSELLER', img: 'https://images.unsplash.com/photo-1582650625119-3a31f8fa2699?auto=format&fit=crop&w=600&q=80' },
    { id: 52, cat: 'adventure', title: 'Krushnai Water Park Splash Pass', venue: 'Donje Gaon: Sinhagad Pune', date: 'Daily Passes', price: 700, banner: 'POPULAR', img: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80' },
    { id: 53, cat: 'adventure', title: 'Wet N Joy Water Park & Waves', venue: 'Lonavala: Pune Highway', date: 'Daily Passes', price: 1399, banner: 'SELLING FAST', img: 'https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=600&q=80' },
    { id: 54, cat: 'adventure', title: 'Imagicaa Theme Park Unlimited Pass', venue: 'Khopoli: Mumbai-Pune Expy', date: 'Daily Passes', price: 1699, banner: 'MUST VISIT', img: 'https://images.unsplash.com/photo-1513889961551-628c1e5e2ee9?auto=format&fit=crop&w=600&q=80' },
    { id: 55, cat: 'adventure', title: 'Della Adventure Park Extreme Pass', venue: 'Lonavala', date: 'Daily Passes', price: 2200, banner: 'THRILL SPECIAL', img: 'https://images.unsplash.com/photo-1522163182402-834f871fd851?auto=format&fit=crop&w=600&q=80' },
    { id: 56, cat: 'adventure', title: 'Magic Mountain Thrill Rides Pass', venue: 'Lonavala', date: 'Daily Passes', price: 1250, img: 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=600&q=80' },
    { id: 57, cat: 'adventure', title: 'Tandem Paragliding Experience', venue: 'Kamshet: Pune Outskirts', date: 'Weekends Active', price: 3200, img: 'https://images.unsplash.com/photo-1508614589041-895b88991e3e?auto=format&fit=crop&w=600&q=80' },
    { id: 58, cat: 'adventure', title: 'Kundalika White Water Rafting', venue: 'Kolad Adventure Camp', date: 'Sat, 17 Oct', price: 1800, img: 'https://images.unsplash.com/photo-1530866495561-507c9faab2ed?auto=format&fit=crop&w=600&q=80' },
    { id: 59, cat: 'adventure', title: 'Night Trek & Stargazing Camping', venue: 'Rajmachi Fort: Lonavala', date: 'Sat, 24 Oct', price: 1350, img: 'https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=600&q=80' },
    { id: 60, cat: 'adventure', title: 'ATV Dirt Bike Off-Roading', venue: 'Pawna Lake Camp: Pune', date: 'Daily Passes', price: 1500, img: 'https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=600&q=80' },

    // 7. AMUSEMENT PARKS
    { id: 61, cat: 'amusement', title: 'Diamond Water Park Day Pass', venue: 'Lohegaon: Pune', date: 'Daily Passes', price: 899, banner: 'LOHEGAON SPECIAL', img: 'https://images.unsplash.com/photo-1582650625119-3a31f8fa2699?auto=format&fit=crop&w=600&q=80' },
    { id: 62, cat: 'amusement', title: 'Krushnai Water Park Pass', venue: 'Donje Gaon: Sinhagad Pune', date: 'Daily Passes', price: 700, img: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80' },
    { id: 63, cat: 'amusement', title: 'Wet N Joy Water Park', venue: 'Lonavala', date: 'Daily Passes', price: 1399, banner: 'WAVE POOL', img: 'https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=600&q=80' },
    { id: 64, cat: 'amusement', title: 'Imagicaa Theme Park Unlimited Pass', venue: 'Khopoli: Mumbai-Pune Expy', date: 'Daily Passes', price: 1699, banner: 'BEST THEME PARK', img: 'https://images.unsplash.com/photo-1513889961551-628c1e5e2ee9?auto=format&fit=crop&w=600&q=80' },
    { id: 65, cat: 'amusement', title: 'Della Adventure Park All-Access', venue: 'Lonavala', date: 'Daily Passes', price: 2200, img: 'https://images.unsplash.com/photo-1522163182402-834f871fd851?auto=format&fit=crop&w=600&q=80' },
    { id: 66, cat: 'amusement', title: 'Magic Mountain Thrill Park', venue: 'Lonavala', date: 'Daily Passes', price: 1250, img: 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=600&q=80' },
    { id: 67, cat: 'amusement', title: 'Water Kingdom Splash Day', venue: 'Gorai: Mumbai', date: 'Daily Passes', price: 1199, img: 'https://images.unsplash.com/photo-1582650625119-3a31f8fa2699?auto=format&fit=crop&w=600&q=80' },
    { id: 68, cat: 'amusement', title: 'EsselWorld Bird Park & Rides', venue: 'Mumbai', date: 'Daily Passes', price: 899, img: 'https://images.unsplash.com/photo-1513889961551-628c1e5e2ee9?auto=format&fit=crop&w=600&q=80' },
    { id: 69, cat: 'amusement', title: 'Wonderla Park Unlimited Access', venue: 'Bengaluru', date: 'Daily Passes', price: 1499, img: 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=600&q=80' },
    { id: 70, cat: 'amusement', title: 'Snow World Indoor Sub-Zero Park', venue: 'Phoenix Marketcity: Pune', date: 'Daily Passes', price: 650, banner: 'INDOOR SNOW', img: 'https://images.unsplash.com/photo-1517299321531-3264a16e8e02?auto=format&fit=crop&w=600&q=80' },

    // 8. ART & CRAFTS
    { id: 71, cat: 'art', title: 'Sip & Paint Canvas Gathering', venue: 'Koregaon Park Cafe: Pune', date: 'Sat, 17 Oct', price: 1200, banner: 'INCLUDES MATERIAL', img: 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80' },
    { id: 72, cat: 'art', title: 'Pottery Painting & Glaze Art', venue: 'Kalakar Studio: Pune', date: 'Sun, 25 Oct', price: 900, img: 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?auto=format&fit=crop&w=600&q=80' },
    { id: 73, cat: 'art', title: 'Lippan Art Mud & Mirror Craft', venue: 'FC Road Art House: Pune', date: 'Sat, 07 Nov', price: 1100, banner: 'TRADITIONAL', img: 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=600&q=80' },
    { id: 74, cat: 'art', title: 'Tie-Dye Fabric Fashion Workshop', venue: 'Viman Nagar: Pune', date: 'Sat, 14 Nov', price: 800, img: 'https://images.unsplash.com/photo-1528459801416-a9e53bbf4e17?auto=format&fit=crop&w=600&q=80' },
    { id: 75, cat: 'art', title: 'Mandala Art Therapy Session', venue: 'Baner Cultural Space: Pune', date: 'Sun, 22 Nov', price: 650, img: 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=600&q=80' },
    { id: 76, cat: 'art', title: 'Macrame Wall Hanging Handcraft', venue: 'Aundh Creative Hub: Pune', date: 'Sat, 28 Nov', price: 950, img: 'https://images.unsplash.com/photo-1528459801416-a9e53bbf4e17?auto=format&fit=crop&w=600&q=80' },
    { id: 77, cat: 'art', title: 'Alcohol Ink Glass Art Class', venue: 'Kothrud Studio: Pune', date: 'Sat, 05 Dec', price: 1350, img: 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80' },
    { id: 78, cat: 'art', title: 'Portrait Oil Painting Masterclass', venue: 'Deccan Gymkhana: Pune', date: 'Sun, 13 Dec', price: 1600, img: 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80' },
    { id: 79, cat: 'art', title: 'Ceramic Plate Hand-Molding', venue: 'Bhavan Art Wing: Pune', date: 'Sat, 19 Dec', price: 1050, img: 'https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?auto=format&fit=crop&w=600&q=80' },
    { id: 80, cat: 'art', title: 'Diya & Lantern Craft Festival', venue: 'Swargate Cultural Center: Pune', date: 'Sun, 27 Dec', price: 400, banner: 'FESTIVE', img: 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=600&q=80' }
];