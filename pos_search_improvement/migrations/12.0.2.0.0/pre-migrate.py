# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    # Migrate product_multi_barcode to product_ean13
    cr.execute("""
        INSERT INTO product_ean13 (name, product_id)
        SELECT barcode, product_id FROM product_multi_barcode
    """)
