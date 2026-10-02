import 'package:flutter_test/flutter_test.dart';
import 'package:money_maintainer_mobile/features/money/presentation/money_page.dart';
void main(){testWidgets('money page renders',(tester)async{await tester.pumpWidget(const MaterialApp(home:MoneyPage(accessToken:'')));expect(find.text('Money'),findsOneWidget);});}
