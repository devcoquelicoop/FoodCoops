import logging

from odoo import models, api, fields, _
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_warning_member_state(self):
        IrConfig = self.env["ir.config_parameter"]
        warning_member_state = (
            safe_eval(IrConfig.sudo().get_param("warning_member_state")) or {}
        )
        member_state = {}
        if not (
            self.cooperative_state
            and self.cooperative_state in warning_member_state
        ):
            member_state = warning_member_state.get("none", {})
        else:
            member_state = warning_member_state.get(self.cooperative_state, {})
        return (
            member_state.get("alert", ""),
            member_state.get("message", ""),
            member_state.get("css-class", ""),
        )

    public_avatar = fields.Boolean(
        "Public Avatar", help="Public your avatar in website", default=True
    )
    public_mobile = fields.Boolean(
        "Public Mobile", help="Public your mobile in website", default=False
    )
    public_email = fields.Boolean(
        "Public Email Address",
        help="Public your email address on website",
        default=False,
    )

    @api.multi
    def action_create_new_user(self):
        """
        Function to activate the User Creation Form
        """
        self.ensure_one()

        res = super(ResPartner, self).action_create_new_user()
        context = res.get("context", {})
        portal_group = self.env.ref("base.group_portal")
        # memberspace group
        memberspace_group = self.env.ref("coop_memberspace.group_memberspace")
        context.update(
            {
                "default_groups_id": [
                    (6, 0, [portal_group.id, memberspace_group.id])
                ]
            }
        )
        return res

    @api.multi
    def create_memberspace_user(self):
        """
        This function is used to create user for existing partner when installing
        module coop_memberspace
        """
        members_dont_have_user = self.filtered(lambda r: not r.related_user_id)
        # portal group
        portal_group = self.env.ref("base.group_portal")
        # memberspace group
        memberspace_group = self.env.ref("coop_memberspace.group_memberspace")
        Users = self.env["res.users"].with_context(
            no_check_validate_email=True
        )
        context = self.env.context.copy()
        context.update(
            {
                "default_groups_id": [
                    (6, 0, [portal_group.id, memberspace_group.id])
                ]
            }
        )
        vals = Users.with_context(context).default_get(list(Users._fields.keys()))
        for member in members_dont_have_user:
            already_email = self.env["res.partner"].search(
                [("email", "=", member.email), ("id", "!=", member.id)]
            )
            if already_email:
                _logger.error(
                    _(
                        "Another user is already registered"
                        + " using this email address."
                    )
                )
                continue
            sql = """
                SELECT id
                FROM res_users
                WHERE login = '%s'
                LIMIT 1
            """
            self.env.cr.execute(sql, member.email)
            user = self.env.cr.fetchone()
            if user:
                user = Users.browse(user[0])
            if not user:
                vals.update(
                    {
                        "partner_id": member.id,
                        "name": member.name,
                        "login": member.email,
                        "email": member.email,
                        "image": member.image,
                    }
                )
                # Users.with_context(no_reset_password=True).create(vals)
                Users.create(vals)
            elif user.active:
                user.partner_id = member.id
        return True

    @api.model
    def cron_create_user_for_members(self):
        members = self.search(
            [("is_member", "=", True), ("email", "!=", False)]
        )
        members.create_memberspace_user()

    @api.model
    def get_partner_gender_website(self):
        if self.gender == "male":
            return _("Man")
        elif self.gender == "female":
            return _("Female")
        return _("Other")
