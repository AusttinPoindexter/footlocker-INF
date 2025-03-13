import argparse
import inspect
import json
from fastly import (
    upload_fastly_dictionary_entries,
    remove_fastly_dictionary_entries,
    upload_fastly_acl_entries,
    remove_all_acl_entries,
    remove_acl_entries,
    backup_fastly_dictionary,
    backup_acl,
    remove_old_fastly_dictionary_entries,
    remove_all_dictionary_entries
)
from logger import write_to_logfile, error_handler, line_number, print_value_info

# Define the available operations
OPERATIONS = {
    "add_entries_to_dictionary": upload_fastly_dictionary_entries,
    "remove_entries_from_dictionary": remove_fastly_dictionary_entries,
    "add_entries_to_acl": upload_fastly_acl_entries,
    "remove_all_acl_entries": remove_all_acl_entries,
    "remove_acl_entries": remove_acl_entries,
    "backup_fastly_dictionary": backup_fastly_dictionary,
    "backup_acl": backup_acl,
    "remove_old_fastly_dictionary_entries": remove_old_fastly_dictionary_entries,
    "remove_all_dictionary_entries": remove_all_dictionary_entries
}


def parse_key_value_pairs(pairs_str):
    try:
        return dict(pair.split(":") for pair in pairs_str.split(","))
    except Exception as e:
        raise argparse.ArgumentTypeError(f"Invalid key:value pair format: {pairs_str}")


def main():
    args = parse_arguments()
    # Debugging: Print args
    print("Received arguments:", vars(args))

    if args.operation in OPERATIONS:
        operation = OPERATIONS[args.operation]
        operation_signature = inspect.signature(operation)
        operation_parameters = operation_signature.parameters

        # Prepare the arguments to pass to the operation
        operation_arguments = {}
        for parameter_name, parameter in operation_parameters.items():
            if (
                parameter_name in vars(args)
                and getattr(args, parameter_name) is not None
            ):
                operation_arguments[parameter_name] = getattr(args, parameter_name)

        try:
            # Call the operation with the prepared arguments
            operation_success = operation(**operation_arguments)
            if not operation_success:
                error_message = f"Operation, {args.operation}, has failed."
                error_handler(error=error_message, line_num=line_number())
                raise Exception(error_message)
        except Exception as e:
            raise Exception(e)
    else:
        error_message = (
            f"Operation, '{args.operation}', does not exist or is unavailable."
        )
        error_handler(error=error_message, line_num=line_number())
        raise Exception(error_message)


def parse_arguments():
    help_text = f"Available Operations are:\n"
    for operation in OPERATIONS:
        help_text += f"* {operation}\n"
    parser = argparse.ArgumentParser(description="Fastly Power Tools")

    parser.add_argument("--operation", type=str, required=True, help=help_text)

    parser.add_argument("--api_key", type=str, required=True, help="Fastly API Key")

    parser.add_argument(
        "--service_name", type=str, required=True, help="The name of the Fastly Service"
    )

    parser.add_argument(
        "--dictionary_name", required=False, type=str, help="Name of Fastly Dictionary"
    )

    parser.add_argument(
        "--acl_name",
        required=False,
        type=str,
        help="Name of Fastly Access Control List",
    )

    parser.add_argument(
        "--input_dictionary",
        required=False,
        type=parse_key_value_pairs,
        help="""
        Comma separated key:value pairs
        'key1:value1,key2:value2'
        """,
    )

    parser.add_argument(
        "--dictionary_items",
        nargs="+",
        required=False,
        type=str,
        help="""
        List of keys, separated by a space: --dictionary_items 1234 2345 3456 4567
        """,
    )

    parser.add_argument(
        "--ips",
        nargs="+",
        required=False,
        type=str,
        help="""
        List of IPs/CIDRs separated by a space: --dictionary_items 192.168.50.1:20, 192.168.1.1
        """,
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
