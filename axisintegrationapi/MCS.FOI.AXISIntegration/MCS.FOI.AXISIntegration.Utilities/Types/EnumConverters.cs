using System;

namespace MCS.FOI.AXISIntegration.Utilities.Types
{
    public static class EnumConverters
    {
        /// <summary>
        /// Generic int to enum converter
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <param name="sender"></param>
        /// <returns></returns>
        public static T ToEnum<T>(this int sender) where T : struct
        {
            return (T)Enum.ToObject(typeof(T), sender);
        }
    }
}
