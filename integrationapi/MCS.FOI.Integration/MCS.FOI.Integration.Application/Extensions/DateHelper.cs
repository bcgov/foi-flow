using System.Globalization;

namespace MCS.FOI.Integration.Application.Helpers
{
    public static class DateHelper
    {
        private const string DateFormat = "MMMM dd, yyyy"; // Output format (March 07, 2025)

        /// <summary>
        /// Safely formats a nullable DateTime to a string. Returns an empty string if null.
        /// </summary>
        public static string FormatDate(DateTime? date)
        {
            return date.HasValue
                ? date.Value.ToString(DateFormat, CultureInfo.InvariantCulture)
                : string.Empty;
        }

        /// <summary>
        /// Parses a date string and returns a formatted date string.
        /// Returns an empty string if the input is null, empty, or invalid.
        /// </summary>
        public static string FormatDate(string? dateString)
        {
            if (string.IsNullOrWhiteSpace(dateString))
                return string.Empty;

            if (DateTime.TryParse(dateString, CultureInfo.InvariantCulture, DateTimeStyles.None, out DateTime parsedDate))
            {
                return parsedDate.ToString(DateFormat, CultureInfo.InvariantCulture);
            }

            return string.Empty; // Return empty string if parsing fails
        }

        /// <summary>
        /// Returns today's date formatted as "MMMM dd, yyyy".
        /// </summary>
        public static string GetTodayDate() => DateTime.Now.ToString(DateFormat, CultureInfo.InvariantCulture);
    }
}
