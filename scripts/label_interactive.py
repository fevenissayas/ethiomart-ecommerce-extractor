import os
import re # Import regex for potential punctuation cleanup during reconstruction

def reconstruct_message_from_tokens(tokens):
    """
    Reconstructs a readable message string from a list of subword tokens.
    Handles '##' prefixes by joining without spaces.
    Aims to provide good context, though might not be 100% identical to original
    due to cleaning or tokenizer-specific spacing.
    """
    reconstructed_parts = []
    for token in tokens:
        if token.startswith('##'):
            reconstructed_parts.append(token[2:]) # Remove '##' and append
        elif token in ['#', ',', '.', ':', ';', '?', '!', '(', ')', '[', ']', '{', '}', '-', '/']: # Handle common punctuation
            # Append punctuation directly to the previous token if there's one, no leading space
            if reconstructed_parts:
                last_part = reconstructed_parts.pop()
                reconstructed_parts.append(last_part + token)
            else:
                reconstructed_parts.append(token)
        else:
            # Add a space before the token, unless it's the very first part
            if reconstructed_parts and not reconstructed_parts[-1].endswith((' ', '\n')): # Avoid double spaces
                reconstructed_parts.append(' ')
            reconstructed_parts.append(token)
    
    reconstructed_text = "".join(reconstructed_parts)
    
    # Basic cleanup for potential extra spaces around punctuation if any
    reconstructed_text = re.sub(r'\s([.,:;?!])', r'\1', reconstructed_text)
    reconstructed_text = re.sub(r'\s+', ' ', reconstructed_text).strip()
    return reconstructed_text

def interactive_labeling_from_token_file(input_token_file_path, output_conll_path):
    """
    Reads a file with tokens on new lines (blank lines separate messages),
    interactively prompts for CoNLL labels after displaying the reconstructed message,
    and saves to an output CoNLL file.

    Args:
        input_token_file_path (str): Path to the input text file with tokens on new lines.
        output_conll_path (str): Path to save the labeled data in CoNLL format.
    """
    try:
        VALID_LABELS = {'O', 'B-PRODUCT', 'I-PRODUCT', 'B-LOC', 'I-LOC', 'B-PRICE', 'I-PRICE'}

        print(f"\nStarting interactive labeling from '{input_token_file_path}'.")
        print("Valid labels: O, B-Product, I-Product, B-LOC, I-LOC, B-PRICE, I-PRICE, B-CONTACT_INFO, I-CONTACT_INFO")
        print("Type 'skip' to skip the rest of the current message (and label remaining tokens 'O').")
        print("Type 'exit' to save current progress and stop labeling.")
        print("Type 'restart_message' to restart labeling the current message.")
        print("-" * 60)

        current_message_tokens = []
        message_count = 0
        
        with open(input_token_file_path, 'r', encoding='utf-8') as f_in, \
             open(output_conll_path, 'w', encoding='utf-8') as f_out:
            
            for line_num, line in enumerate(f_in):
                stripped_line = line.strip()

                if not stripped_line: # Blank line indicates end of message
                    if current_message_tokens: # If there were tokens collected for the message
                        message_count += 1
                        
                        # --- RECONSTRUCT AND DISPLAY THE MESSAGE CONTEXT ---
                        reconstructed_message = reconstruct_message_from_tokens(current_message_tokens)
                        print(f"\n--- Message {message_count} ---")
                        print(f"Reconstructed Message Context: {reconstructed_message}")
                        print("\n--- Start Labeling Tokens ---")
                        # ----------------------------------------------------

                        labeled_tokens_for_message = []
                        temp_tokens_for_restart = list(current_message_tokens) # Store a copy for restart_message
                        
                        for token_idx, token in enumerate(temp_tokens_for_restart):
                            while True:
                                label = input(f"  Token {token_idx + 1}/{len(temp_tokens_for_restart)}: '{token}' -> Enter label: ").strip()

                                if label.lower() == 'skip':
                                    print(f"Skipping remainder of current message. Labeling remaining as 'O'.")
                                    # Label current token and all subsequent tokens as 'O'
                                    for t_idx in range(token_idx, len(temp_tokens_for_restart)):
                                        labeled_tokens_for_message.append(f"{temp_tokens_for_restart[t_idx]}\tO")
                                    break # Break from token loop

                                elif label.lower() == 'exit':
                                    print("\nExiting labeling session. Saving current progress.")
                                    if labeled_tokens_for_message: # Save any partially labeled message
                                        f_out.write("\n".join(labeled_tokens_for_message))
                                        f_out.write("\n\n")
                                    return # Exit the function entirely

                                elif label.lower() == 'restart_message':
                                    print(f"\nRestarting labeling for Message {message_count}. (Previous labels for this message cleared)")
                                    labeled_tokens_for_message = [] # Clear collected labels for this message
                                    # Reset the input file pointer to the beginning of this message.
                                    # This is complex in a simple line-by-line read.
                                    # For interactive restarts of the *current* message, it's often easier
                                    # to just break the inner loop and loop over the same 'temp_tokens_for_restart' from start.
                                    token_idx = -1 # Reset token index to -1 to start from 0 in next iteration
                                    break # Break from inner validation loop to restart token loop
                                    
                                if label in VALID_LABELS:
                                    labeled_tokens_for_message.append(f"{token}\t{label}")
                                    break # Valid label, move to next token
                                else:
                                    print(f"Invalid label '{label}'. Valid labels are: {', '.join(VALID_LABELS)}. Try again.")
                            
                            # If we broke from the inner loop due to 'skip' or 'restart_message', break outer loop as well
                            if label.lower() in ['skip', 'restart_message']:
                                break

                        # --- After labeling all tokens for the message ---
                        f_out.write("\n".join(labeled_tokens_for_message))
                        f_out.write("\n\n") # Double newline to separate messages in CoNLL format
                        print(f"Message {message_count} labeled and saved.")
                        current_message_tokens = [] # Reset for next message
                    else:
                        f_out.write("\n") # Write blank line if consecutive blanks or leading blank
                    continue # Move to next line in input file

                # This is a token line, add it to the current message's tokens list
                token = stripped_line
                current_message_tokens.append(token)
            
            # --- Handle any remaining tokens if the file ends without a final blank line ---
            if current_message_tokens:
                message_count += 1
                print(f"\n--- End of Message {message_count} (End of File) ---")
                reconstructed_message = reconstruct_message_from_tokens(current_message_tokens)
                print(f"Reconstructed Message Context: {reconstructed_message}")
                print("\n--- Start Labeling Tokens ---")
                
                labeled_tokens_for_message = []
                for token_idx, token in enumerate(current_message_tokens):
                    while True:
                        label = input(f"  Token {token_idx + 1}/{len(current_message_tokens)}: '{token}' -> Enter label: ").strip()
                        if label.lower() == 'skip':
                            for t_idx in range(token_idx, len(current_message_tokens)):
                                labeled_tokens_for_message.append(f"{current_message_tokens[t_idx]}\tO")
                            break
                        elif label.lower() == 'exit':
                            if labeled_tokens_for_message:
                                f_out.write("\n".join(labeled_tokens_for_message))
                                f_out.write("\n\n")
                            return
                        if label in VALID_LABELS:
                            labeled_tokens_for_message.append(f"{token}\t{label}")
                            break
                        else:
                            print(f"Invalid label '{label}'. Try again.")

                f_out.write("\n".join(labeled_tokens_for_message))
                f_out.write("\n\n")

        print(f"\nLabeling session complete. All messages processed from '{input_token_file_path}'.")
        print(f"Labeled data saved to: '{output_conll_path}'")

    except FileNotFoundError:
        print(f"Error: The input token file '{input_token_file_path}' was not found. Please check the path.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

# --- Main execution ---
if __name__ == "__main__":
    input_file = "data/labeled/unlabeled_conll.txt"
    output_file = "data/labeled/ner_conll_amharic.txt"

    os.makedirs("data/labeled", exist_ok=True)

    interactive_labeling_from_token_file(input_file, output_file)
