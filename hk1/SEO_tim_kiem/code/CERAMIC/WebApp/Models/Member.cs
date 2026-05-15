using System.ComponentModel.DataAnnotations.Schema;

namespace WebApp.Models
{
    [Table("Member")]
    public class Member
    {
        [Column("MemberId")]
        public string Id { get; set; } = null!;

        public string Name { get; set; } = null!;

        public string GivenName { get; set; } = null!;

        public string? Surname { get; set; }

        public string Email { get; set; } = null!;

        public byte[] Password { get; set; } = null!;

        public Role Role { get; set; }
    }
}
