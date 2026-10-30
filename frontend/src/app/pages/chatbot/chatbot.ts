
import { Component, ChangeDetectorRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Chatbot as ChatbotService } from '../../services/chatbot';

interface ChatMessage {
  text: string;
  sender: 'user' | 'bot';
}

@Component({
  selector: 'app-chatbot',
  imports: [FormsModule],
  templateUrl: './chatbot.html',
  styleUrl: './chatbot.css',
})
export class Chatbot {

  userMessage = '';

  messages: ChatMessage[] = [
    {
      text: 'Hello! I am your Vendor Reliability Platform chatbot. How can I help you?',
      sender: 'bot'
    }
  ];

  isLoading = false;

  constructor(private chatbotService: ChatbotService,private cdr: ChangeDetectorRef) {}

  sendMessage(): void {

    const message = this.userMessage.trim();

    if (!message || this.isLoading) {
      return;
    }

    this.messages.push({
      text: message,
      sender: 'user'
    });

    this.userMessage = '';
    this.isLoading = true;

    this.chatbotService.sendMessage(message).subscribe({
      next: (response) => {

        this.messages.push({
          text: response.reply,
          sender: 'bot'
        });

        this.isLoading = false;
        this.cdr.markForCheck();
      },

      error: (error) => {

        console.error('Chatbot API error:', error);

        this.messages.push({
          text: 'Sorry, something went wrong. Please try again.',
          sender: 'bot'
        });

        this.isLoading = false;
        this.cdr.markForCheck();
      }
    });
  }
}
