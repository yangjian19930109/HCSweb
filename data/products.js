var PRODUCTS_DATA = [
    {
        id: "1030837",
        title: "1030837 分动箱电机",
        cat: "车用马达",
        subCat: "其他马达",
        desc: "用于Jeep自由光、大指挥官分动箱PTU执行器电机",
        url: "product-1030837.html",
        images: ["images/products/1030837.png"],
        detail: "",
        detail_images: []
    },
    {
        id: "1030896",
        title: "1030896 节气门电机",
        cat: "车用马达",
        subCat: "节气门马达",
        desc: "12V有刷直流节气门马达，用于Jeep自由光、大指挥官",
        url: "product-1030896.html",
        images: ["images/products/1030896.png"],
        detail: "",
        detail_images: []
    },
    {
        id: "1031001",
        title: "1031001涡轮增压执行器电机",
        cat: "车用马达",
        subCat: "涡轮增压执行器马达",
        desc: "涡轮增压执行器电机，用于大通，长城等品牌车涡轮增压器，供给海拉等知名总成商，高温耐受，精确行程控制",
        url: "product-1031001.html",
        images: ["images/products/1031001_740ae642.png", "images/products/1031001_9d80fd19.png", "images/products/1031001_33101c8b.png"],
        detail: "涡轮增压执行器电机，用于大通、长城等品牌车涡轮增压器，供给海拉等知名总成商。高温耐受，精确行程控制。",
        detail_images: ["images/products/1031001_4d235314.png", "images/products/1031001_78613dac.jpg"]
    },
];



















// ========== Fuse.js 模糊搜索实例 ==========
var fuse = null;

function initFuse() {
    if (typeof Fuse === 'undefined') return false;
    fuse = new Fuse(PRODUCTS_DATA, {
        keys: [
            { name: 'title',    weight: 0.6 },
            { name: 'desc',     weight: 0.3 },
            { name: 'subCat',   weight: 0.1 }
        ],
        threshold: 0.4,
        distance: 100,
        includeScore: true,
        minMatchCharLength: 1,
        shouldSort: true
    });
    return true;
}

function doSearch(query) {
    if (!query || query.trim().length < 1) return [];

    var q = query.trim();

    // 优先使用 Fuse.js 模糊搜索
    if (fuse) {
        var results = fuse.search(q);
        return results.slice(0, 10).map(function(r) {
            return {
                cat: r.item.cat,
                subCat: r.item.subCat,
                title: r.item.title,
                desc: r.item.desc,
                url: r.item.url,
                score: r.score
            };
        });
    }

    // 降级：纯静态子串匹配
    var lower = q.toLowerCase();
    return PRODUCTS_DATA.filter(function(item) {
        return item.title.toLowerCase().indexOf(lower) >= 0 ||
               item.desc.toLowerCase().indexOf(lower) >= 0 ||
               item.subCat.toLowerCase().indexOf(lower) >= 0;
    }).slice(0, 10);
}

// 页面加载时自动初始化
(function() {
    if (typeof Fuse !== 'undefined') {
        initFuse();
    }
})();