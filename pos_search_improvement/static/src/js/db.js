odoo.define('pos_search_improvement.db', function (require) {
    "use strict";

    // We need to load both features first
    var PosDB = require('pos_accented_search');
    var PosMultiEanDB = require('pos_multi_ean.db');

    PosDB.include({

        // Overide _product_search_string to allow searching product by
        // Internal Reference and Barcode Only
        _product_search_string: function (product) {
            var res = []
            if (product.barcode) {
                res.push(product.barcode);
            }
            // Set Multi barcode for product
            if (product.multi_ean_json) {
                res.concat(JSON.parse(product.multi_ean_json));
            }
            // Default code
            if (product.default_code) {
                res.push(product.default_code);
            }
            str = res.join('|')
            str = product.id + ':' + str.replace(/:/g, '') + '\n';
            // Compatibility with accented_search
            return this.normalize_characters(str)
        },

        search_product_in_category: function (category_id, query) {
            var res = this._super(category_id, query);
            var results = [];
            for (var i = 0; i < res.length; i++) {
                if (res[i].barcode === query || res[i].default_code === query || res[i].description_sale === query || res[i].description === query) {
                    results.push(res[i]);
                } else if (this.product_by_barcode[query]) {
                    results.push(this.product_by_barcode[query]);
                } else {
                    break;
                }
            }
            return results;
        },

    });
});
