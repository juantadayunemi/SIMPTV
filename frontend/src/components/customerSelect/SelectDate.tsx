import { Calendar } from "lucide-react";

interface SelectDateProps {
    date: string;
    onDateChange: (date: string) => void;
}

export default function SelectDate({ date, onDateChange }: SelectDateProps) {

    return (

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Calendar size={20} className="text-gray-400 flex-shrink-0" />
          <input
            type="date"
            value={date}
            onChange={(e) => onDateChange(e.target.value)}
            className="flex-1 sm:flex-none px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyDown={(e) => e.preventDefault()}
          />
        </div>
    )

}