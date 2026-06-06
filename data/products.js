var PRODUCTS_DATA = [
    {
        id: "1030837",
        title: "1030837 分动箱电机",
        cat: "车用马达",
        subCat: "其他马达",
        desc: "用于Jeep自由光、大指挥官分动箱PTU执行器电机",
        url: "product-1030837.html",
        images: [],
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
        images: [],
        detail: "",
        detail_images: []
    },
    {
        id: "throttle-001",
        title: "节气门马达",
        cat: "车用马达",
        subCat: "节气门马达",
        desc: "电子节气门控制，高精度位置反馈，响应快速",
        url: "products.html#tab-motor",
        images: [],
        detail: "",
        detail_images: []
    },
    {
        id: "waste-valve-001",
        title: "废气阀马达",
        cat: "车用马达",
        subCat: "废气阀马达",
        desc: "废气再循环系统用，耐用高温环境，精确控制",
        url: "products.html#tab-motor",
        images: [],
        detail: "",
        detail_images: []
    },
    {
        id: "turbo-001",
        title: "涡轮增压执行器马达",
        cat: "车用马达",
        subCat: "涡轮增压执行器马达",
        desc: "可变几何涡轮增压器用，双向动作，55mm行程",
        url: "products.html#tab-motor",
        images: [],
        detail: "",
        detail_images: []
    },
    {
        id: "door-lock-001",
        title: "车门锁马达",
        cat: "车用马达",
        subCat: "车门锁马达",
        desc: "汽车中央门锁执行器，低功耗静音",
        url: "products.html#tab-motor",
        images: [],
        detail: "",
        detail_images: []
    },
    {
        id: "epb-001",
        title: "EPB马达",
        cat: "车用马达",
        subCat: "EPB马达",
        desc: "电子驻车制动系统专用，高可靠性",
        url: "products.html#tab-motor",
        images: [],
        detail: "",
        detail_images: []
    },
    {
        id: "v4nc-001",
        title: "V4NC 直流电机",
        cat: "车用马达",
        subCat: "EPB马达",
        desc: "EPB系统专用，体积小、扭矩大、寿命超10万次循环",
        url: "products.html#tab-motor",
        images: [],
        detail: "",
        detail_images: []
    },
    {
        id: "dc971-001",
        title: "DC971 无刷电机",
        cat: "车用马达",
        subCat: "其他马达",
        desc: "无刷设计、低功耗、高效率，适合新能源汽车应用",
        url: "products.html#tab-motor",
        images: [],
        detail: "",
        detail_images: []
    },
    {
        id: "x4-001",
        title: "X4 齿轮电机",
        cat: "车用马达",
        subCat: "其他马达",
        desc: "集成齿轮减速结构，高输出扭矩，适用汽车座椅调节",
        url: "products.html#tab-motor",
        images: [],
        detail: "",
        detail_images: []
    },
    {
        id: "appliance-001",
        title: "家用电器马达系列",
        cat: "家用电器及电动工具马达",
        subCat: "家用电器马达",
        desc: "洗衣机、冰箱、空调等家电用马达",
        url: "products.html#tab-appliance",
        images: [],
        detail: "",
        detail_images: []
    },
    {
        id: "tool-001",
        title: "电动工具马达",
        cat: "家用电器及电动工具马达",
        subCat: "电动工具马达",
        desc: "电钻、锯、抛光机等电动工具用高性能马达",
        url: "products.html#tab-appliance",
        images: [],
        detail: "",
        detail_images: []
    },
    {
        id: "switch-001",
        title: "微动开关系列",
        cat: "微动开关",
        subCat: "微动开关",
        desc: "精密微动开关，寿命长，触点可靠",
        url: "products.html#tab-switch",
        images: [],
        detail: "",
        detail_images: []
    },
    {
        id: "1031001",
        title: "1031001涡轮增压执行器电机",
        cat: "车用马达",
        subCat: "涡轮增压执行器马达",
        desc: "涡轮增压执行器电机，用于大通，长城等品牌车涡轮增压器，供给海拉等知名总成商，高温耐受，精确行程控制",
        url: "products.html#tab-motor",
        images: ["images/products/1031001_79babaa5.png"],
        detail: "",
        detail_images: ["images/products/1031001_9715449c.png"]
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